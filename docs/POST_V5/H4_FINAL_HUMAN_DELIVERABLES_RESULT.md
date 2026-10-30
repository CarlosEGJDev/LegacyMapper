# H4 — Entregables humanos finales: resultado

Estado final: **`H4_READY_FOR_HUMAN_REVIEW`** (suite completa verde, §9). Sin commit, push ni tag. No se inició H5. La aceptación humana **no** se declara (H5 la posee): la muestra está preparada (§12). Ronda única (R1 integrada); no hubo R2.

Sincronización previa (solo higiene de estado): H1/H2/H3 = `CLOSED`, revisión humana H3 = `APPROVED`, `next` = H4 → ahora `H5_REAL_IST_VALIDATION_AND_CLOSURE`.

## 1. Arquitectura
Paquete nuevo `legacy_documenter/deliver/` (solo presentación y empaquetado; sin inferencia, sin escáner, sin proveedor):
* `markdown.py` — modelo de bloques + parser estricto del subconjunto Markdown que emite H2 (encabezados, párrafos, citas, listas, tablas, código, enlaces, escapes). Un nombre vacío en la evidencia se declara («nombre vacío en la evidencia»).
* `html.py` — renderer HTML estático determinista, CSS y un JS local opcional (filtro de tablas + búsqueda por título).
* `pdf.py` — escritor PDF 1.4 propio, sin dependencias (fuentes estándar WinAnsi; diagramas SVG H3 como vectores).
* `package.py` — orquestación: gate de baseline H1 → H2 + H3 desde el baseline persistido (área temporal) o consumidos → bloques → HTML/PDF → manifest.
* `cli/deliver_command.py` — adaptador fino; ruta en `router.py`/`parser.py`/`main.py`; opciones clasificadas en `fingerprints/configuration.py` (RUNTIME_ONLY).
Un solo modelo de bloques alimenta HTML y PDF, así que ambos no pueden divergir en contenido. Las 10 superficies se componen de páginas H2 + diagramas H3 + notas semánticas fijas; ninguna cifra se calcula de nuevo (salen del modelo H2/H3).

## 2. CLI
`python main.py deliver <output-existente> [--output] [--audience]… [--docs-dir] [--visuals-dir] [--ai-run [--include-ai]] [--area]… [--project]… [--flow-id]… [--top-areas N (10) | --all-areas] [--max-nodes] [--max-children] [--no-pdf] [--pdf-row-cap N (30)] [--verify-evidence fast|hash]`. Por defecto escribe `<baseline>\human_package`. Inválido → `DELIVER_INPUT_INVALID`, exit 4, sin escribir. `--output` vacío o paquete H4 previo (se reemplaza limpio); nunca el baseline. Paquete visual de otro baseline → `VISUALS_STALE`. Alcance visual por defecto: N áreas más activas + todos sus proyectos + un flujo representativo por área. Detalle: `docs/V5/V5_OPERATIONS_GUIDE.md` §14.

## 3. Estructura del paquete
`index.html`, `about.html`, `DELIVERABLES_MANIFEST.json`, `executive/`, `functional/`, `technical/` (páginas H2, README→index), `deliverables/` (10 superficies + índice), `visuals/` (SVG, modelo JSON, página HTML por diagrama con alternativa textual, `VISUALS_MANIFEST.json`), `assets/` (style.css, site.js, search-index.js), `pdf/`.

## 4. Entregables
| Superficie | Composición | Límite semántico declarado |
|---|---|---|
| SYSTEM_OVERVIEW | resumen ejecutivo H2 + mapa del sistema H3 | propósito de negocio no determinado |
| MODULE_MAP | capas + enlaces a áreas/proyectos + mapas | módulo = solución/proyecto/capa inferida; sin módulos de negocio |
| FUNCTIONAL_AREAS | `functional/areas` + mapas de área | área = solución, no función de negocio |
| USE_CASES | «no hay casos de uso confirmados…» + flujos observables como representación más cercana | solo muestra casos con `kind` de caso de uso: canónico (aprobado) o IA aparte, no aprobada |
| BUSINESS_FLOWS | procesos H2 + diagramas de flujo | se llaman «flujos observables» |
| ARCHITECTURE_OVERVIEW / PROJECT_LAYER_MAP | vista técnica H2 + mapas de dependencias/capas | capa = inferencia estructural |
| DATA_INTERACTIONS | resumen funcional + datos + mapas de interacción | tipo inferido del nombre |
| EXTERNAL_INTEGRATIONS | tabla: externa confirmada / plataforma / sin clasificar / no resuelto + integraciones H2 | lo sin clasificar no es integración confirmada |
| KNOWN_UNRESOLVED_AREAS | cuánto no se sabe + narrativa H2 + diagramas con nodos no resueltos | no resuelto ≠ ausencia; también en Inicio y en la navegación |
Cada entrada del manifest lleva `support` (p. ej. `NO_CONFIRMED_USE_CASES`, `OBSERVABLE_FLOWS_ONLY`).

## 5. HTML
Estático, sin CDN ni dependencias, enlaces relativos, UTF-8, `<details>` plegables (abiertos), TOC, migas, selector de audiencia (menú), leyenda en cada pie, SVG con «abrir tamaño completo», página por diagrama con enlaces resumen↔detalle, impresión (CSS `@media print`). El script es opcional.

## 6. PDF
4 PDF (`System_Overview`, `Executive`, `Functional`, `Technical_Overview`). Portada con leyenda, contenido, marcadores, «Página X de N». Diagramas H3 vectoriales en páginas apaisadas; los altos se cortan entre nodos (≤6 partes); un diagrama no imprimible legible (<0.42 de escala) se sustituye por nota (0 en IST). Un diagrama no se repite dentro de un PDF. Tablas largas: `--pdf-row-cap`, con declaración «Se muestran N de M filas». Sin marcas de tiempo.

## 7. Estados epistémicos
Una leyenda única (pie de cada página, `about.html`, portada PDF). Cada estado se imprime como texto y con patrón de borde propio (continuo / discontinuo / punteado+«!» / doble+«IA» / grueso+«OK»); los SVG H3 se copian sin tocar. Nada se fortalece: IA nunca confirmada (probado), canónico distinto (probado), rechazadas no se muestran, sin corrida de IA no hay secciones de IA.

## 8. Archivos
Nuevos: `legacy_documenter/deliver/{__init__,markdown,html,pdf,package}.py`, `cli/deliver_command.py`, `tests/test_post_v5_h4_deliver.py`, `docs/POST_V5/H4_DELIVER_INVENTORY.json` (snapshot vivo; módulos 308). Modificados: `cli/{parser,router}.py`, `main.py`, `fingerprints/configuration.py`, `tests/test_v4_1_r0_maintainability_inventory.py`, `README.md`, `docs/V5/V5_OPERATIONS_GUIDE.md` §14, roadmap post-V5 y continuidad, `PROJECT_STATE.json`. Sin cambios en Evidence, analyzer, adapters, review, providers ni H1–H3.

## 9. Pruebas
Nuevas: 46 (`test_post_v5_h4_deliver`): parser (escapes, tablas, vacíos); render HTML (escapado, estados, enlaces relativos, secciones, etiquetas largas); PDF (xref válido, determinismo, texto dentro de página, fallback); semántica con contexto simulado (casos de uso no fabricados, solo `kind` de caso de uso, IA separada, integraciones sin ascenso); extremo a extremo (contrato/manifest con hashes, 10 superficies, 0 enlaces rotos, sin red, landings, referencias cruzadas, estados, no resuelto prominente, activos visuales, PDF, byte-idéntico, docs/visuals consumidos = generados, sin proveedor/escáner/analizador, baseline intacto, rechazos, solo ejecutivo/sin PDF, reemplazo limpio); IA/canónico; resumen→detalle con diagramas descompuestos.
**Suite completa:** **3254 tests, 0 failures, 0 errors, 132 skips** (3208 + 46 nuevos; 774 s). En la corrida completa el único fallo fue el snapshot vivo del inventario (`H4_DELIVER_INVENTORY.json`, desfasado por una edición posterior de `package.py`); se regeneró y se re-ejecutaron inventario + H4 (68 tests OK). Analyzer fingerprint sin cambios.

## 10. Validación IST (baseline persistido `IST_REAL_AI`, sin reanalizar)
| Medida | Resultado |
|---|---|
| Generación (H2+H3+H4) | 35 s |
| HTML / PDF / SVG | 777 / 4 / 399 (1 584 archivos, 14.6 MB) |
| HTML mayor | `visuals/index.html` 99 KB (página H2 mayor: `processes-part-000001` 88 KB) |
| PDF | Executive 13 p · Functional 55 p · System_Overview 49 p · Technical 50 p; mayor 147 KB; 0 diagramas sustituidos por texto |
| Diagramas / parciales | 399 / 11 |
| Enlaces | 16 549 verificados, **0 rotos**, 0 fragmentos faltantes, 0 referencias fuera del paquete |
| Visuales faltantes | 0 |
| Proveedor / escáner / analizador | **0 / 0 / 0** (guardas activas) |
| Baseline (47 529 archivos) | **0 añadidos / 0 eliminados / 0 cambiados** |
| Reejecución | 1 584 archivos byte-idénticos (incluye PDF) |
Revisados visualmente: inicio, entregables, área `slnPREPrevencion_2010`, no resuelto, y páginas PDF (portada, tabla, flujo, dependencias).

## 11. Determinismo
HTML, SVG, JSON, CSS, JS y manifest: byte-idénticos. PDF: byte-idénticos en esta toolchain (sin fechas, `/ID` derivado del contenido); como los flujos se deflatan con zlib, los bytes dependen de la versión de Python/zlib, por eso el manifest registra `content_sha256` sobre los flujos sin comprimir (independiente de la herramienta).

## 12. Muestra de revisión humana (no es aceptación)
`C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\` — `package\` completo (abrir `index.html`), `pdf\`, `REVIEW_GUIDE.md` con las 8 preguntas y el área `slnPREPrevencion_2010`.

## 13. Limitaciones conocidas
* Sin PNG (SVG basta). Sin `use-case-map`/`external-integration-map` (H3: sin evidencia).
* Diagramas por defecto: 10 áreas + sus proyectos (`--all-areas` para todas: ~+3×).
* PDF: tablas acortadas por diseño; fuentes estándar (caracteres fuera de WinAnsi se transliteran); sin enlaces internos entre páginas (remite al HTML); diagramas muy altos en varias páginas apaisadas; el PDF funcional incluye solo 5 áreas con diagramas.
* Verificación visual del PDF hecha con un rasterizador de apoyo propio (sin visor PDF disponible en headless); conviene abrirlos en un visor real durante la revisión.
* Los nombres técnicos (pantallas, eventos, objetos) siguen siendo los del código; capa y tipo de interacción son inferencias.
* El kind de «caso de uso» solo existe si una propuesta lo declara; hoy ninguna lo hace.

## 14. Deuda introducida
Ninguna bloqueante. Candidatos: enlaces internos en el PDF, paginación de índices muy grandes (`visuals/index.html` con `--all-areas`), reducción de cruces de aristas (heredada de H3).

## 15. Git
Cambios sin commitear (H1 + H2 + H3 + H4 acumulados); `prompts/POST_V5/*` sin versionar. Tag `v5` intacto. Sin commit/push/tag (autoridad H4).

## 16. Recomendación
Revisar la muestra con `REVIEW_GUIDE.md` (abrir también los PDF en un visor real); si es conforme, pasar a `H5_REAL_IST_VALIDATION_AND_CLOSURE` y autorizar el commit de H1–H4.

## H4-R3 Final Verification and Closure

Estado final: **`H4_READY_FOR_FINAL_HUMAN_REVIEW`**. Cierre técnico completo; **aprobación humana explícita ausente**, por lo que H4 **no** se marca `CLOSED` y no se declara aceptación. H5 no iniciado. Sin cambios de código ni tests (ningún defecto de cierre encontrado).

**Higiene del roadmap.** `HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md` §4 «Brecha principal» aún decía «HTML/PDF no productizado» y «proyección visual no implementada»; ahora indica HX-01 = resuelta por H2+H3+H4 (pendiente de aceptación humana en H5), HX-02 = resuelta por H4, HX-03 = resuelta por H3, coherente con §10/§11 y con `PROJECT_STATE.json`. Hechos históricos de V5 sin tocar.

**Verificación del paquete real HTML** (`...post_v5_h4_final_deliverables_review\package`, 777 páginas): las 777 son alcanzables desde `index.html` solo siguiendo enlaces; los 10 entregables alcanzables; 0 referencias de red (HTML/CSS/JS); leyenda de estados en cada pie; no resuelto prominente (recuadro en Inicio, pestaña propia y página «Cuánto no se sabe»); `slnPREPrevencion_2010` (4 diagramas) y `WebPrePrevencion` (3 diagramas) con imágenes existentes; resumen→detalle correcto en 37/37 diagramas descompuestos. Capturas revisadas: Inicio, SYSTEM_OVERVIEW, USE_CASES, EXTERNAL_INTEGRATIONS, KNOWN_UNRESOLVED_AREAS, área y proyecto (renderizado con Edge headless desde `file://`).

**Seguridad semántica** (verificada sobre el texto real): USE_CASES no inventa (sin actores/objetivos; «no hay casos de uso confirmados derivables de la evidencia estática»); FUNCTIONAL_AREAS declara área = solución, no función de negocio; MODULE_MAP «no se inventan módulos de negocio»; EXTERNAL_INTEGRATIONS: cuatro categorías y «sin clasificar no es integración confirmada»; BUSINESS_FLOWS: «no se afirma que representen un flujo de negocio».

**Verificación PDF.** `System_Overview` (49 p, 14 marcadores) y `Functional` (55 p, 24 marcadores): portada con leyenda de estados, contenido, «Página X de N», tablas sin recortes, diagramas vectoriales legibles, sin grafo microscópico (0 sustituidos). **Limitación honesta:** no hay visor PDF real disponible; la verificación visual se hizo con un rasterizador de apoyo propio y extracción con `pypdf` (estructura/xref válidos), así que **no** se afirma verificación en visor real; el revisor humano debe abrirlos. Observación menor: algún encabezado queda al pie de página antes de su contenido (p. ej. «Qué no debe inferirse»); cosmético, no bloquea.

**Baseline/IST** (sin reanálisis, desde el output persistido): delta determinista 0/0/0 sobre 47 529 archivos; proveedor 0, escáner 0, analizador 0; 16 549 enlaces, 0 rotos, 0 fragmentos faltantes, 0 visuales faltantes, 0 referencias fuera del paquete.

**Determinismo.** Regeneración desde el baseline en un directorio nuevo: 1 584 archivos (HTML, SVG, JSON, manifest, PDF) byte-idénticos a la muestra de revisión.

**Suite completa final** (último paso que modifica el árbol; `python -X utf8 -m unittest discover -s tests`): **3254 tests, 0 failures, 0 errors, 132 skips, 689.607 s, exit code 0** (`OK (skipped=132)`), sobre el árbol final exacto; supera el fallo de snapshot visto en la corrida anterior de H4-R1.

**Estado de aceptación humana.** Pendiente: no hay aprobación explícita del revisor del paquete HTML/PDF. Si el revisor la da, el único cambio de estado restante es `H4 = CLOSED`, `h4_human_review = APPROVED`.

**Git.** Cambios H1–H4 sin commitear; sin commit/push/tag; `prompts/POST_V5/*` sin versionar; tag `v5` intacto.

**Recomendación.** Abrir `package\index.html` y los PDF en un visor real con `REVIEW_GUIDE.md`; con aprobación explícita, cerrar H4 y pasar a H5; el commit de H1–H4 requiere autorización aparte.

