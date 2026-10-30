# H4 — Final Human Layout and Overflow Polish: resultado

Estado: **`H4_FINAL_HUMAN_LAYOUT_AND_OVERFLOW_POLISH = READY_FOR_HUMAN_APPROVAL`**. **H4 = HUMAN_APPROVAL_PENDING** (no cerrado). **H5 = NOT_STARTED**. Sin commit, push ni tag.

Solo presentación. Sin cambios en Evidence, interpretación de IA, relaciones, rutas, contratos `ai/`, escáner ni analizador.

## 1. Reglas de layout cambiadas
* **Medición real:** se auditó el PDF generado (texto y rectángulos contra el ancho útil de página) y los SVG (texto dentro de su caja, cajas dentro del `viewBox`). Antes de los cambios el PDF principal no tenía texto fuera de página; los defectos reales eran otros (abajo).
* **Leyenda de estados** de las páginas de diagrama en vertical medía 611 pt en una página útil de 523 pt: ahora se parte en dos líneas (`deliver/pdf.py`).
* Encabezados de sección (nivel 1–2) reservan espacio para algunas líneas de su contenido (antes «6. Limitaciones» quedaba con una línea al pie y el resto en una página casi vacía en el PDF ejecutivo).

## 2. Escalado de diagramas
* **Flujo simple** (`behavior/flowboxes.py`): cajas de 150 (antes 176) y márgenes menores → 1078 de ancho (antes 1282); el PDF imprime a escala ≈ 0,66–0,72 (antes 0,60). Una columna se ensancha (hasta 196) solo cuando un identificador no se puede partir sin cortarlo por caracteres; más aire entre el texto y la etiqueta de estado.
* **Orientación elegida por diagrama** (`_figure_pages`): vertical u horizontal según necesite menos páginas y dé mayor escala; un diagrama cabe en una página si la escala sigue ≥ 0,62; mínimo absoluto 0,5 (antes 0,42). Si hay que cortar, las partes cortan solo entre filas y **cada parte repite el nodo origen «Vista» con sus conectores** (antes quedaban flechas colgando de la página anterior y cajas cortadas). `ucPreEstadisticasAccidentes` (8 filas) pasa de 3 páginas partidas a 1.
* **Reconstrucciones**: una página si la escala ≥ 0,62 (antes 0,5); si no, partes **balanceadas** (sin parte final corta), cortes solo entre controles. `ucPreMantEmpadronamiento` (1306 de alto) pasa de escala 0,54 en una página a 2 partes a 0,69; las demás representativas siguen en una página.
* Ningún SVG se deforma (misma escala en x e y) y todos quedan centrados.

## 3. Tablas
Los identificadores largos se parten por palabras (límites camelCase y separadores `. / \ _`), no por caracteres: antes `ucPreCargaArchivoAsignac|ion`, `ucPreCatastroDiagRiesgoE|rgonomico`; ahora `ucPre|Carga|Archivo|Asignacion`. Esto también estrecha las columnas mínimas, así que el catálogo de 121 vistas se reparte mejor. El cortador por caracteres queda solo como último recurso.

## 4. Rutas técnicas y identificadores largos
Tabla «Acción / Ruta»: la ruta se parte en pasos (`->`) y símbolos (`PPRE_` `GES_` `JERARQUIA.`), sin bajar de la tipografía técnica normal. En SVG (`behavior/svgtext.py`) el ajuste de texto usa también límites camelCase (`ucPreEstadisticas|Accidentes`).

## 5. HTML
`deliver/html.py`: `<wbr>` tras separadores y en límites camelCase de identificadores largos; celdas y `code` con `overflow-wrap:break-word` (ya no `anywhere`); `pre` con `pre-wrap`; badges de estado que pueden envolver y con `max-width:100%`; tarjetas y KPI con `minmax(min(…,100%),1fr)`; imágenes/figuras/callouts con `max-width:100%`; `.table-wrap` con scroll horizontal local. Texto corrido conserva `anywhere` solo como último recurso. El cuerpo no tiene scroll horizontal por contenido.

## 6. PDF
Ver §1–§3. Verificación sobre el PDF generado: `LegacyMapper.pdf` 40 páginas, `executive.pdf` 9; 0 elementos fuera del ancho útil en ambos; 0 incidencias en los 38 SVG (texto dentro de su caja y de su `viewBox`).

## 7. Vistas representativas inspeccionadas
Rasterizando las páginas del PDF con un renderizador propio (cabecera de diagnóstico, no incluido en el repositorio): `ucPreMantJerarquia2`, `ucBusSuc`, `ucPreMantEmpadronamiento`, `ucPreEstadisticasAccidentes`, `ucPreConActxProd` (reconstrucción, flujo simple, rutas, tablas), diagrama de invocaciones, catálogo ancho de 121 vistas, ruta técnica larga y PDF ejecutivo completo.

## 8. Proveedor, escáner/analizador, fuente
Llamadas al proveedor: **0**. Escáner/analizador/Evidence: **no ejecutados**; fuente: **no leída**. Se reutilizó la línea base y las respuestas de IA persistidas de `runs\manual_final` (copiadas a la corrida nueva). `ai/` del paquete nuevo es **idéntico byte a byte** al de `manual_final_clean_human`.

## 9. Pruebas
Nuevas: `tests/test_post_v5_h4_layout_polish.py` (14): envoltura por camelCase, tablas sin partir identificadores, `<wbr>` en HTML, reglas CSS de contención, cajas del flujo contienen su texto y el lienzo contiene las cajas, ensanchado en vez de partir, nodo origen etiquetado, páginas de figura dentro del ancho útil, partes de un flujo repiten el origen, leyenda vertical, partes de wireframe balanceadas, ruta larga sin desbordar. Ajustada: guarda de HTML con etiquetas largas (`anywhere` solo en texto corrido). Dirigidas: 202 OK.

## 10. Suite completa
`python -X utf8 -m unittest discover -s tests`: **3533 tests, 0 failures, 0 errors, 132 skips, 489 s**. Las corridas previas del ciclo mostraron 4 fallos por `<wbr>` en comparaciones de texto HTML y por el inventario de Gate C: se ajustaron las pruebas (comparan sin `<wbr>`), se regeneró la clave `inventory` de `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json` y `PROJECT_STATE.json` (estado de ronda) se actualizó; luego la suite completa quedó en verde.

## 11. Ruta de revisión
`C:\PruebasLegacyMapper\FinalValidation\runs\manual_final_layout_polish\package\` — abrir `human\index.html`, `human\LegacyMapper.pdf`, `human\executive.pdf` (opcional: `human\guide\assets\ucpreestadisticasaccidentes-flujo.svg`, `ucpremantempadronamiento-wireframe.svg`).

## 12. Limitaciones
* La sonda de navegador (Edge sin cabeza) no arrancó en este entorno: la contención HTML está verificada por reglas CSS y pruebas estructurales, no por una medición de `scrollWidth` en un navegador.
* El PDF se verificó por medición del flujo de dibujo y rasterización propia, no con un visor externo.
* Texto de diagramas impresos a escala 0,62–0,72 (≈ 7–8 pt); el HTML los ofrece a tamaño completo.
* Identificadores en minúscula sin límites internos (p. ej. `txcargacomboactecoxprofesional`) solo se parten por caracteres si superan el ancho máximo de caja.

## 13. Estado
`H4_FINAL_HUMAN_LAYOUT_AND_OVERFLOW_POLISH = READY_FOR_HUMAN_APPROVAL` · `H4 = HUMAN_APPROVAL_PENDING` · `H5 = NOT_STARTED`. Sin commit, push ni tag.
