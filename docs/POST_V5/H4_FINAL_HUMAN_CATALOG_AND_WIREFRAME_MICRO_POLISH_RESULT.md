# H4 — Final Human Catalog and Wireframe Micro-Polish: resultado

Estado: **`H4_FINAL_HUMAN_CATALOG_AND_WIREFRAME_MICRO_POLISH = READY_FOR_FINAL_MANUAL_RUN`**. **H4 = HUMAN_APPROVAL_PENDING** (no cerrado). **H5 = NOT_STARTED**. Sin commit, push ni tag.

## 1. Catálogo
`behavior/render.py`: el catálogo del apéndice (guía por defecto) pasa de 9 columnas a **4 descriptivas**: *Vista · Título visible · Qué parece hacer · Uso observable* (las vistas con capítulo siguen marcadas con ●). En el ejecutivo el mismo catálogo de 4 columnas queda plegado (HTML) y fuera del PDF. Desaparecen del PDF: «Cómo se llega», «Acciones», «¿Lee?», «¿Escribe?», «¿Abre otra?» (los valores «26 vistas la abren», «4», «sí/no», «0/1/3»).

## 2. Métricas de cobertura
La sección «Mediciones de cobertura» y la tabla de fidelidad por capacidad **ya no están en el PDF**. En HTML solo existen dentro del bloque plegado **«Metadatos del análisis (diagnóstico)»** (junto con el detalle antiguo de relaciones por vista), rotulado como metadato de análisis, y se omiten del PDF. Permanecen íntegras en el modelo (`measurements`), en `internal/` y en `ai/`.
Se conservan los conteos de alcance con nombres (p. ej. «La solución agrupa 3 proyectos: …»).

## 3. Estrategia de etiquetas de wireframe
`behavior/wireframe.py`:
* `display_label(control)` (solo para dibujar; el modelo conserva etiqueta/identificador crudos): texto visible → icono/identificador normalizado (`[iconoAsignar]`→`Asignar`, `[icono buscar]`→`Buscar`, `iconoDesasociar.gif`→`Desasociar`, `btnEliminar`→`Eliminar`) → `Icono` neutro; no se inventa significado.
* Ancho mínimo por celda según la palabra más larga de sus botones (+ icono + relleno): las celdas se **rebalancean** quitando holgura de las más anchas en lugar de reducir el texto; nunca se rota ni se apila texto vertical.
* Resultado en `ucPreMantJerarquia2`: `Asignar`, `Desasociar`, `Buscar` en horizontal (antes pilas de un carácter por línea). Revisión de los 5 SVG representativos: sin pilas verticales (≤ 1 texto de un carácter por SVG = la marca «v» de listas desplegables), sin etiquetas recortadas ni solapes.

## 4. Verdad semántica
`ai/` (7 archivos) **byte-idéntico** a la ronda anterior; `AI_INTERPRETATION_MANIFEST.json` idéntico; `internal/behavioral/explanations.json` difiere solo en el SVG de los wireframes (verificado: igual con los SVG excluidos). Sin cambios en estados, rutas, relaciones ni procedimientos.

## 5. Proveedor, escáner/analizador, fuente
Llamadas al proveedor: **0**. Escáner/analizador/Evidence: **no ejecutados**. Fuente: **no leída** (se re-validan las respuestas de IA guardadas sobre el baseline persistido). PDF guía: 44 → 42 páginas.

## 6. Pruebas
Nuevas en `tests/test_post_v5_h4_noise_pdf_polish.py` (`CatalogAndLabelTests`, 6): catálogo PDF solo con columnas descriptivas y todos los nombres de vista, métricas de cobertura ausentes del PDF y presentes (plegadas) en HTML/modelo, conteos de alcance con nombres permitidos, etiquetas de icono legibles (y `Icono` sin invención), wireframes sin pilas verticales, PDF determinista. Ajustada una aserción de `test_post_v5_h4_content_polish` (ancla de mediciones → bloque de metadatos).

## 7. Suite completa
`python -X utf8 -m unittest discover -s tests`, ejecutada **una vez** con los cambios estables: **3500 tests, 0 failures, 0 errors, 132 skips, 824 s**. (Antes se regeneró la clave `inventory` de `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json`.)

## 8. Ruta de revisión
`C:\PruebasLegacyMapper\Resultados\h4_final_catalog_wireframe_polish\package\` — abrir `human\index.html`, `human\LegacyMapper.pdf`, `human\executive.pdf`.

## 9. Estado
`H4_FINAL_HUMAN_CATALOG_AND_WIREFRAME_MICRO_POLISH = READY_FOR_FINAL_MANUAL_RUN` · `H4 = HUMAN_APPROVAL_PENDING` · `H5 = NOT_STARTED`. Siguiente paso: corrida manual final como usuario final; si se aprueba, prompt formal de cierre de H4.
