# H3 — Proyecciones visuales estructuradas: resultado

Estado final: **`H3_READY_FOR_HUMAN_REVIEW`** (suite completa verde, §12). Sin commit, push ni tag. No se inició H4. La aceptación humana **no** se declara: la muestra está preparada (§10).

## 1. Inventario empírico de relaciones (IST real `IST_REAL_AI` + muestras H2)
| Relación | Fuente persistida | Clasificación | Cómo se dibuja |
|---|---|---|---|
| solución → proyecto | `evidence/solutions.json` (`SOL-`), `index/solutions.json` | SAFE_FOR_VISUALIZATION | CONFIRMADO |
| proyecto → capa | regla estructural H2 | SAFE_IF_LABELED_INFERRED | grupo/nodo INFERIDO (nunca confirmado) |
| proyecto → proyecto (`ProjectReference`) | `index/projects.json` (`PRJ-`) | SAFE_FOR_VISUALIZATION | CONFIRMADO |
| proyecto → biblioteca interna | proyectos del repositorio | SAFE_FOR_VISUALIZATION | CONFIRMADO |
| proyecto → biblioteca de plataforma | lista de plataforma | SAFE_IF_LABELED_INFERRED | grupo INFERIDO |
| proyecto → biblioteca sin clasificar | referencia confirmada, naturaleza desconocida | NOT_SAFE_YET como afirmación de naturaleza | grupo NO RESUELTO (no se trata como tercero confirmado) |
| pantalla → evento → manejador → método | `functional_flows` (aristas con `confidence` y `evidence_refs`) | SAFE_FOR_VISUALIZATION | se conserva la confianza de cada arista |
| método → operación de datos → procedimiento | idem (`DAO-…`) | SAFE_FOR_VISUALIZATION | CONFIRMADO |
| método → llamada no resuelta | idem (`CALL-…`) | SAFE_FOR_VISUALIZATION | NO RESUELTO |
| pantalla → objeto de datos | flujos con `StoredProcedure`/`SQL` | SAFE_FOR_VISUALIZATION | arista CONFIRMADA |
| tipo de interacción (lectura/registro/…) | nombre de la operación (clasificador H2) | SAFE_IF_LABELED_INFERRED | **grupo INFERIDO**, nunca arista de hecho |
| propuesta de IA / canónico → evidencia | corrida de IA (solo con `--ai-run --include-ai`) | AI_ONLY_IF_LABELED | IA o CANÓNICO, siempre aparte |
| agrupación de negocio / casos de uso | — | NOT_SAFE_YET | **no se dibuja** (use-case-map y external-integration-map no se implementaron: no hay evidencia limpia) |
Todas las referencias de los 12–18 diagramas de IST (3 719) se verificaron una a una: **0 sin resolver** (ids `PRJ-`/`SOL-`/`FLOW-`/`EP-`/`DAO-`/`CAL-` vía `legacy_ref`, nombres de procedimiento).

## 2. Contrato del modelo visual (`legacy_documenter/visuals/model.py`)
`VisualProjection` = `contract/contract_version`, `id`, `kind`, `title`, `audience`, `scope`, `nodes[]` (`id,label,type,status,source_refs,group,metadata`), `edges[]` (`id,source,target,relation,status,source_refs,label,metadata`), `groups[]`, `legend`, `provenance`, `unresolved`, `partial {partial,included_count,omitted_count,reason}`, `metadata`. Sin marcas de tiempo; ids = hash estable de claves canónicas; JSON ordenado. `validate_projection` rechaza: estado inválido, ids duplicados, extremos colgantes, aristas CONFIRMADAS/CANÓNICAS sin `source_refs`, aristas INFERIDAS sin regla, **aristas más fuertes que su extremo más débil** (nada que toque IA o un nodo no resuelto es «confirmado»), diagramas parciales sin motivo. El renderer solo lee el modelo ya validado: una IA podría como máximo enriquecer el *modelo*.

## 3. Tipos implementados
`system-map` (sistema → áreas → capas; área → proyectos → capa), `project-layer-map`, `dependency-map`, `observable-flow`, `data-interaction-map`. Alcances: sistema, área (solución), proyecto, flujo.

## 4. Renderer
SVG determinista (`svg.py`): enteros, texto escapado (XML) y sin caracteres de control, ajuste de línea a 26 caracteres con hasta 3 líneas y «…» (el texto completo queda en `<title>`), leyenda en cada diagrama, `role="img"` + `<title>/<desc>`, marcadores de flecha por estado, nota *Parcial* cuando corresponde. Sin dependencias, sin generación de imágenes por IA. PNG/HTML opcionales no se implementaron (SVG + JSON bastan para H4).

## 5. Layout
Interno y determinista (`layout.py`): capas por camino más largo sobre el DAG (ciclos rotos por DFS en orden `(label,id)`), orden por grupo → baricentro (2 barridos estables) → `(label,id)`, coordenadas enteras, cajas de grupo contiguas. Misma entrada → mismo SVG byte a byte (probado, también con permutación de nodos/aristas).

## 6. Semántica visual de estados
CONFIRMADO borde continuo · INFERIDO discontinuo (`7 4`) · NO RESUELTO punteado (`2 3`) + «!» · IA doble borde `8 3 2 3` + «IA - NO APROBADA» · CANÓNICO borde grueso + «OK CANÓNICO». Cada nodo imprime su estado como texto; la leyenda va en cada SVG: legible en escala de grises/PDF.

## 7. Escala
Cota de 40 nodos/diagrama (`--max-nodes`): lo excedente se agrega en un nodo «+N …» (los nombres quedan en `metadata.items` del `.json`), el diagrama se marca `partial` con `included_count/omitted_count/reason`; en flujos, las llamadas no resueltas de un método se agregan (>3) y cuentan contra la cota; los nodos Proyecto/Clase sin relaciones propias se pliegan en grupos/etiquetas. Aristas duplicadas se fusionan uniendo sus referencias. Diagramas sin nodos no se escriben y se reportan en `selection.skipped_empty`.

## 8. CLI
`python main.py visuals <output-existente> [--output] [--area]… [--project]… [--flow-id]… [--top-areas N|--all-areas] [--kind]… [--max-nodes N] [--ai-run --include-ai] [--verify-evidence]`. Se eligió un comando propio (no `docs --visuals`) porque `docs` escribe Markdown por audiencia y `visuals` escribe SVG + modelos + manifest con controles de alcance propios; ambos comparten el gate de baseline de H1. Sin `--area/--project/--flow-id`: sistema + `--top-areas` (3) áreas más activas con un flujo representativo. No reescanea, no reconstruye Evidence y nunca resuelve un provider. Salida: `visuals/…/<tipo>.svg|.json` + `VISUALS_MANIFEST.json` (rutas relativas y deterministas, hashes, conteos, parcialidad: listo para H4).

## 9. Archivos cambiados
Producción nueva: `legacy_documenter/visuals/{__init__,model,layout,svg,builders,package}.py`, `cli/visuals_command.py`. Modificados: `cli/{parser,router}.py`, `main.py`, `fingerprints/configuration.py` (clasificación de opciones). Tests: `tests/test_post_v5_h3_visuals.py` (nuevo, 28); ajustado `test_v4_1_r0_maintainability_inventory.py` (301 módulos; snapshot vivo → `docs/POST_V5/H3_VISUALS_INVENTORY.json`). Docs: `README.md`, `docs/V5/V5_OPERATIONS_GUIDE.md` §13, roadmap post-V5 y continuidad, `PROJECT_STATE.json`. Sin cambios en Evidence, analyzer (`f05b2de4…`), adapters, review, provider ni esquemas.

## 10. Validación
**Pequeña** (fixture de 3 proyectos): 6 diagramas (los 5 tipos), todos válidos y trazables (`PRJ-`, `SOL-`, `FLOW-`, `DAO-`), SVG bien formados, reejecución byte-idéntica, baseline intacto, fuente eliminada.
**IST real** (output persistido, sin reanalizar): carga del contexto 11.4 s (carga del índice de ~951 MB; la generación en sí toma 0.1 s); paquete de validación con 17 diagramas (sistema; áreas `slnPREPrevencion_2010`, `SlnPENProcesoResoluciones` —la más dependiente y con más no resuelto—; proyectos `WebPREPrevencion` y `blMEDUPoliprogramado`; 3 flujos: más operaciones de datos, más llamadas no resueltas y uno con interpretación de IA Fake): SVG más grande 48 KB; máx. 41 nodos / 80 aristas; 9 parciales (agregados, nada descartado); **3 719 referencias, 0 sin resolver**; **0 invocaciones de scanner/extractor/`full`**; **0 resoluciones de provider**; **baseline determinista: 0 añadidos / 0 eliminados / 0 cambiados** (47 529 archivos, tamaño+mtime).
**Muestra de revisión humana** (no es aceptación): `C:\PruebasLegacyMapper\Resultados\post_v5_h3_visual_review\` — `system-map.svg`, `project-layer-map.svg`, `dependency-map.svg`, `observable-flow.svg`, `data-interaction-map.svg` (todos del área `slnPREPrevencion_2010`), mapa a nivel sistema, un flujo con muchas llamadas no resueltas, un flujo con una interpretación de IA (provider Fake) y `package/` completo, más `REVIEW_GUIDE.md` con las cinco preguntas. Se revisaron visualmente renders de los SVG (mapa de capas, interacción con datos, flujos pequeño y muy grande, flujo con IA).

## 11. Pruebas
* Nuevas: 28 (`test_post_v5_h3_visuals`): contrato/forma; validador (8 violaciones); propagación de estados; grafo vacío; ids estables (incluida permutación); escape XML y control; etiquetas largas; estado por patrón + texto; mismo input → mismo SVG; trazabilidad de todos los diagramas; ids estables entre construcciones independientes; los 5 builders (contención, capas inferidas, referencias, flujo con no resuelto, categorías como grupo inferido); IA solo a petición y nunca confirmada; canónico distinto tras aprobación humana; agregación sin pérdida; paquete + manifest + rutas relativas + SVG bien formados; reejecución byte-idéntica; sin scanner/provider; baseline intacto; selección de alcance; rechazos sin escribir; ayuda del CLI; variante de escritura (`GRABA_…` → grupo inferido «Registro / creación»).
* Dirigidos (inventario, fingerprints, review V5.7, H3): 149 OK.
* **Suite completa:** ver la línea final de §12.

## 12. Totales de la suite completa
**3188 tests, 0 failures, 0 errors, 132 skips** (3160 + 28 nuevos; 734 s). Analyzer fingerprint sin cambios (`f05b2de4…`).

## 13. Limitaciones conocidas
* Sin PNG ni HTML (H4 empaquetará); sin `use-case-map` ni `external-integration-map` (la evidencia no sostiene casos de uso ni servicios externos).
* Los diagramas muy grandes (flujos de cientos de nodos) se muestran parciales y densos: legibles pero con cruces de aristas (el layout no minimiza cruces más allá de un baricentro).
* La capa y el tipo de interacción son inferencias; las copias de proyecto (`Backup`) aparecen como proyectos separados.
* La interpretación de IA solo se dibuja en `observable-flow` y solo con `--ai-run --include-ai`; en la muestra proviene de un provider Fake.
* El ancho de un diagrama crece con la profundidad del flujo (columnas de 350 px).

## 14. Deuda introducida
Ninguna bloqueante. Candidatos: reducción de cruces de aristas; PNG/HTML embebible (H4); decidir si `full` debería generar un paquete visual por defecto (hoy opt-in).

## 15. Git
Cambios sin commitear (H1 + H2 + H2-R2 + H3 acumulados); prompts `prompts/POST_V5/*` sin versionar. Tag `v5` intacto.

## 16. Recomendación
Revisar la muestra visual y decidir: aprobar H1–H3 y autorizar commit/push; siguiente: `H4_FINAL_HUMAN_DELIVERABLES` (no iniciado).

## H3-R2 Targeted Visual Readability Correction

Estado: **`H3_READY_FOR_FINAL_HUMAN_REVIEW`** (suite completa registrada abajo). Alcance: solo legibilidad por layout y descomposición; sin tocar Evidence, analyzer, adapters, provider, review ni H1/H2, sin tipos de diagrama nuevos y sin inferencia de negocio. **No se declara aceptación humana.**

**Hallazgo de la revisión humana (se conserva):** system-map = PASS · project-layer-map = PASS · observable-flow = PASS con observación de legibilidad (flujos demasiado horizontales) · dependency-map = PARCIAL (maraña de cruces) · data-interaction-map = PARCIAL (muchas aristas pantalla → operación).

**Cambios exactos**
* **Descomposición determinista** (`visuals/decompose.py`, nuevo), preferida a enrutado inteligente:
  * *dependency-map* denso (>24 aristas o ya agregado) → **resumen** (proyectos, referencias entre proyectos y un nodo agregado por clase de biblioteca —interna / plataforma / sin clasificar— con el conteo por proyecto en cada arista y los miembros exactos en la metadata) + **detalles** por proyecto en foco (sus referencias de proyecto y, por clase, sus bibliotecas en trozos de ≤14). Las clases conservan su estado (interna CONFIRMADA, plataforma INFERIDA, sin clasificar NO RESUELTA).
  * *data-interaction-map* denso (>24 relaciones o >12 pantallas) → **resumen** (grupos de ≤8 pantallas → categorías inferidas del nombre, con el conteo exacto de relaciones; categoría INFERIDA/NO RESUELTA, aristas con sus `source_refs`) + **detalles** por categoría, en trozos de ≤10 objetos, con las aristas pantalla → objeto CONFIRMADAS.
  * Alcances pequeños se devuelven sin cambios (misma proyección de H3).
* **Contrato de descomposición** (reutiliza el modelo; solo se añadió un bloque opcional `decomposition` que no aparece en diagramas no descompuestos): `role` (summary/detail), `parent_projection_id`, `part_index`, `part_count`, `scope`, `included_count`, `omitted_count`, `aggregation_reason`, `children`/`child_count` en el resumen, más `focal_project` / `action`. `partial` conserva su significado de H3 (esta vista agrega/omite nodos concretos); un resumen descompuesto **no** es `partial` porque el detalle existe en los hijos. Cota `--max-children` (30): lo no expandido se registra (`omitted_count`, `unexpanded_projects`, motivo) y sus relaciones siguen en la metadata del resumen.
* **Layout** (`layout.py`): los diagramas con más de 4 columnas se envuelven en **bandas** (lectura izquierda→derecha, arriba→abajo; título «Sección i de n»; las continuaciones entre bandas se dibujan con ruta ortogonal por el hueco entre bandas). Diagramas de ≤4 columnas no cambian. Sin motores externos ni aleatoriedad.
* **Render** (`svg.py`): etiquetas de relación idénticas repetidas (>6, en diagramas de 13–60 aristas) no se imprimen en cada arista y la omisión se declara bajo el diagrama; los conteos numéricos nunca se suprimen. Diagramas de ≤12 aristas o de >60 renderizan exactamente igual que antes.
* **Paquete/manifest**: `<tipo>.details/<foco>--<parte>.svg|.json` bajo el resumen (nombres y orden estables), `parent_id`, `decomposition` y `metrics` (`canvas_width/height`, `edges_per_node`, `max_out_degree`) por diagrama; `selection.decomposed_diagrams/detail_diagrams/max_children`. CLI: `--max-children`.

**Antes / después (IST real, área `slnPREPrevencion_2010` y proyecto `WebPREPrevencion`)**
| Diagrama | Antes | Después |
|---|---|---|
| dependency-map (área) | 1374×1796, 21 nodos, 32 aristas, máx. salida 20, *parcial* | resumen 1024×505, 6 nodos, 9 aristas, máx. salida 5 + 11 detalles (≤15 nodos, ≤14 aristas de salida) |
| dependency-map (proyecto) | 1374×2458, 29 nodos, 28 aristas, máx. salida 28, *parcial* | resumen 820×761, 6 nodos, 5 aristas + 5 detalles |
| data-interaction-map | 820×2469, 41 nodos, 30 aristas, máx. salida 8, *parcial* | resumen 820×689, 8 nodos, 9 aristas + 6 detalles (≤20 nodos, ≤17 aristas, máx. salida 4) |
| observable-flow (largo) | 2074×2254–2318 | 1374×2472–2536 (en secciones; ancho cabe en un navegador normal) |
| observable-flow (corto) | 2074–2424 px de ancho | 1374×711–720 |
| system-map (área / sistema), project-layer-map | — | **byte-idénticos** al H3 revisado (md5 `013e2c28…`, `fb3767e4…`) |
Medidas reales de densidad (no un número inventado de cruces): aristas por nodo y salida máxima por panel; en los detalles más grandes quedan ≤14–17 aristas por diagrama.

**Diagramas generados y relaciones.** Paquete de validación IST: 40 diagramas (4 resúmenes + 28 detalles + sistema, capas, mapas del sistema y flujos), SVG más grande 47 KB, 5 diagramas `partial` (antes 9). **Preservación de relaciones:** dependencias resumen = detalles = **44 = 44**; interacciones con datos **34 = 34**; todas las referencias (3 848) resuelven (**0 sin resolver**); 0 archivos faltantes. Reejecución del paquete byte-idéntica.

**Validación IST y entorno:** baseline determinista **0 añadidos / 0 eliminados / 0 cambiados**; **0** resoluciones de provider; **0** invocaciones de scanner/extractor/`full`; contexto + generación 11.6 s.
**Muestra refrescada:** `C:\PruebasLegacyMapper\Resultados\post_v5_h3_visual_review\` (`dependency-map.svg` y `data-interaction-map.svg` como resúmenes, `dependency-map-details/`, `data-interaction-map-details/`, `observable-flow.svg` en secciones, ejemplos, `package/` y `REVIEW_GUIDE.md` actualizada con las cinco preguntas).

**Tests.** Nuevos `tests/test_post_v5_h3_r2_readability.py` (20): descomposición determinista de dependencias y de interacciones; resumen pequeño/detalles acotados; conservación de todas las relaciones (resumen = detalle); cotas de hijos registradas; metadata padre/hijo estable y consistente; estados y `source_refs` sin cambios; categorías inferidas y aristas trazables; envoltura de flujos que conserva el orden lógico (columnas monótonas, nodos sin solapes, ancho ≤1500, ruta ortogonal, NO RESUELTO conservado); flujos cortos sin envolver; system-map y project-layer-map sin artefactos de R2; supresión de etiquetas solo en diagramas densos y nunca de conteos; paquete con nombres/orden estables, manifest con hijos, byte-idéntico; sin provider ni escaneo; baseline intacto; ayuda con `--max-children`. Ajustado el conteo de módulos (302) y el snapshot de inventario.
**Suite completa: 3208 tests, 0 failures, 0 errors, 132 skips** (3188 + 20 nuevos; 607 s). Analyzer fingerprint sin cambios (`f05b2de4…`).

**Limitaciones.** Los resúmenes agregan por diseño (el detalle está en los hijos); los detalles más grandes aún tienen cruces de aristas (no se mide un número de cruces); los flujos muy grandes quedan altos aunque anchos de 1374 px; se omiten hijos más allá de `--max-children` (registrado); la capa y el tipo de interacción siguen siendo inferencias.

**Git.** Cambios sin commitear (H1 + H2 + H3 + H3-R2 acumulados); prompts `prompts/POST_V5/*` sin versionar. Tag `v5` intacto.

**Recomendación.** Revisar la muestra refrescada con las cinco preguntas de la guía; con confirmación final, autorizar commit/push de H1–H3 y pasar a `H4_FINAL_HUMAN_DELIVERABLES`.
