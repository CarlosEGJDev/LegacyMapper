# H4 — Final Human Screen Reconstruction and Narrative Micro-Polish: resultado

Estado: **`H4_FINAL_HUMAN_SCREEN_RECONSTRUCTION_AND_NARRATIVE_MICRO_POLISH = READY_FOR_FINAL_HUMAN_APPROVAL`**. **H4 = HUMAN_APPROVAL_PENDING** (no cerrado). **H5 = NOT_STARTED**. Sin commit, push ni tag.

Solo presentación humana. Diagramas congelados (no se tocó `flowboxes`, mapas ni rutas). Sin cambios en Evidence, IA, `ai/` ni escáner/analizador.

## 1. Cambios en la reconstrucción de pantallas (`behavior/wireframe.py`)
Motor determinista general, no un parche por vista:
* **Ancho mínimo por palabra humana:** una celda nunca es más estrecha que su palabra más larga (etiquetas, botones; cajas de texto ≥ 84), calculado recursivamente también para tablas anidadas. Si hace falta, las celdas hermanas ceden espacio.
* **Símbolos sueltos (`<`, `>>`)**: etiquetas de 1–3 caracteres sin letras ni dígitos se tratan como residuo de maquetación y no se dibujan; el control sigue en el modelo.
* **Columnas de acción:** una tabla anidada compuesta solo por botones/enlaces (y esos símbolos) se simplifica a una columna de botones del mismo ancho; los marcadores de mensaje (`lblMensaje*`) se leen debajo de las acciones y, vacíos, se muestran como marcador discreto en gris, no como título.
* **Etiquetas intermedias** (`Hasta`) y **etiqueta + control** conservan ancho legible; el rebalanceo reparte el exceso entre celdas con holgura.
* **Orden de nombres:** texto visible → nombre semántico de la acción → identificador humanizado (`hypAsignar` → «Asignar», `HypDesasociar` → «Desasociar») → identificador crudo solo si no hay nada mejor. El identificador crudo permanece en `ai/` e `internal/`.
* PDF: el texto SVG con `text-anchor="end"` (p. ej. el «+1» de una grilla con más de 8 columnas) ahora se alinea al borde derecho; antes se dibujaba hacia fuera.

## 2. `ucPreMantJerarquia2` antes / después
Antes: columna central estrecha, «<» y «>» sueltos y apilados («>/>»), `lblMensaje1/2` en celdas estructurales sueltas y botón «Desasociar» solapando celdas. Después: dos botones **[Asignar] / [Desasociar]** alineados, del mismo ancho, sin flechas (la dirección no puede establecerse con seguridad: los glifos originales están desplazados respecto de los botones) y `lblMensaje1/2` debajo. Sin solapes ni recortes.

## 3. `ucBusSuc`
«Criterio» (celda de 14 px) se partía en «Cr / ite / rio»; ahora la celda se ensancha y se lee «Criterio» completo junto a la lista y la caja de texto.

## 4. `ucPreConActxProd`
«Hasta» se partía en «H / as / ta» entre las dos fechas; ahora se lee **[fec_ini]  Hasta  [fec_fin]** en una línea. (Sin «Desde»: el texto del marcado no lo respalda.)

## 5. Procedencia y números de línea
`behavior/humanize.py`, aplicado solo al componer el documento humano (HTML y PDF, guía y ejecutivo): se eliminan `(línea 68)` y `(ventana emergente; línea 12)` de la prosa (25 → 0 en la guía). Las ubicaciones exactas siguen en el modelo compartido, `ai/provenance.json` e `internal/` (`src:archivo:línea`).

## 6. Lenguaje de auditoría
Reglas contextuales, no sustitución ciega: «La evidencia muestra…» → «Se observa…»; «La evidencia confirma/permite/no …» → «El análisis …»; «No se especifica en la evidencia» → «No se especifica»; «con la evidencia estática» → «con el análisis estático»; etc. Los títulos «Evidencia de uso» pasan a **«Uso observable»**. Menciones de «evidencia» en el texto visible de la guía HTML y del PDF: 0 (antes: 7 en el PDF y varias decenas en el HTML, incluidos los títulos «Evidencia de uso»).

## 7. Leyenda de estados
La guía y el ejecutivo muestran solo **Confirmado (azul) / Inferido (naranja) / No resuelto (rojo)**, con color y borde/etiqueta. La portada del PDF y la leyenda al pie de las páginas de diagrama ya no listan «Interpretación de IA» ni «Canónico» (siguen en `ai/` e `internal/` y en el resto de paquetes). Un único aviso introductorio de IA.

## 8. Prueba de que `ai/` e `internal/` conservan la trazabilidad
`ai/` del paquete candidato es **idéntico byte a byte** al de `manual_final_clean_human` (`diff -r`). `internal/behavioral/explanations.json` solo difiere en el SVG de las 5 reconstrucciones. El modelo conserva «línea N» y las referencias `src:archivo:línea` (prueba incluida).

## 9. Páginas inspeccionadas (rasterizadas y vistas)
Guía PDF: portada (leyenda de 3 estados); `ucPreMantJerarquia2` (reconstrucción); `ucBusSuc` (reconstrucción); `ucPreMantEmpadronamiento` (partes 1 y 2); `ucPreEstadisticasAccidentes` (reconstrucción); `ucPreConActxProd` (reconstrucción). Aserciones visuales: sin palabra vertical, sin flechas sueltas, sin solapes, sin etiquetas recortadas, fechas y transferencia legibles. Estructural: 0 elementos fuera del ancho útil en `LegacyMapper.pdf` (40 págs.) y `executive.pdf` (9 págs.); 0 incidencias en los SVG.

## 10. Proveedor / escáner / analizador / fuente
Llamadas al proveedor **0**; escáner **0**; analizador **0**; Evidence **no reconstruida**; fuente **no leída**. Se reutilizó la línea base y las respuestas de IA persistidas.

## 11. Pruebas
Nuevas: `tests/test_post_v5_h4_screen_narrative.py` (14): botones Asignar/Desasociar enteros y sin flechas, mismo ancho/sin solape/rótulo dentro, mensajes debajo, modelo conserva todos los controles, «Criterio» y «Hasta» legibles con ancho mínimo, ninguna palabra partida, sin «(línea N)» ni «Evidencia de uso» en HTML/PDF, las líneas siguen en el modelo, leyenda de 3 estados y un solo aviso de IA, reglas de humanización. Actualizadas las pruebas históricas que fijaban el texto antiguo («Evidencia de uso», «contra la evidencia disponible», «ausencia de evidencia de uso»). Dirigidas: 305 OK.

## 12. Suite completa
`python -X utf8 -m unittest discover -s tests`: **3547 tests, 0 failures, 0 errors, 132 skips, 691 s**. Un intento previo falló solo por el contador de módulos de producción del inventario V4.1 (nuevo módulo `behavior/humanize.py`: 334); se actualizó el pin y la clave `inventory` de la evidencia de Gate C y la suite quedó en verde.

## 13. Ruta de revisión
`C:\PruebasLegacyMapper\FinalValidation\runs\manual_final_h4_candidate\package\human\` — `index.html`, `LegacyMapper.pdf`, `executive.pdf` (reconstrucciones: págs. 6, 11, 17–18, 24, 31 del PDF).

## 14. Limitaciones
PDF verificado con rasterizador propio y mediciones, no con un visor externo; HTML sin medición en navegador (Edge sin cabeza no arranca en este entorno). Los marcadores `lblMensaje*` vacíos se muestran con su identificador en gris tenue: es el único nombre disponible.

## 15. Estado
`H4_FINAL_HUMAN_SCREEN_RECONSTRUCTION_AND_NARRATIVE_MICRO_POLISH = READY_FOR_FINAL_HUMAN_APPROVAL` · `H4 = HUMAN_APPROVAL_PENDING` · `H5 = NOT_STARTED`. No se cierra H4 automáticamente. Sin commit, push ni tag.
