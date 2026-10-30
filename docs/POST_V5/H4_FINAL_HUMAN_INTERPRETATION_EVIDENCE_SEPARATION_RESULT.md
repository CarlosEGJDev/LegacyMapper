# H4 — Final Human Interpretation / Evidence Separation: resultado

Estado: **`H4_FINAL_HUMAN_INTERPRETATION_EVIDENCE_SEPARATION = READY_FOR_HUMAN_APPROVAL`**. **H4 = HUMAN_APPROVAL_PENDING** (no cerrado). **H5 = NOT_STARTED**. Sin commit, push ni tag.

Principio aplicado: **los humanos reciben interpretación; `ai/` e `internal/` conservan la prueba.**

## 1. Qué se quitó del documento humano (HTML y PDF, guía y ejecutivo)
`behavior/render.py`, `behavior/flowboxes.py`, `behavior/prototype.py`:
* IDs de Evidence (`EP-…`, `FLOW-…`, `CALL-…`) y de apoyo determinista (`DAO-…`), también en las etiquetas de rutas, flujos y en los tooltips (`<title>`) de los SVG.
* Referencias a código fuente (`src:…`, archivo:línea). La tabla de mensajes ya no tiene la columna «Línea»; las tablas de invocaciones con «Dónde (archivo:línea)» salen del documento.
* Los bloques «Base de las afirmaciones», «Base del uso observable», «Respaldo de la interpretación», «Referencias y controles», «Evidencia técnica / Trazabilidad de la vista» (como capítulo de evidencia), «Evidencia considerada y convenciones de nombre», «Por qué se eligieron estas vistas», «Fidelidad de la reconstrucción», «Metadatos del análisis (diagnóstico)», «Trazabilidad de la interpretación de IA», la huella de la línea base y el pie de portada del PDF con la huella.
* Proveedor, modelo y número de solicitudes (en la portada, apéndice y PDF).
* Las tablas «Afirmación | Estado» (y «Base») para solución, proyecto, módulos y limitaciones: ahora son tarjetas de color.

## 2. Dónde queda esa información
`product/package.py` (`ai_projections`):
* `ai/knowledge.json` — por vista detallada, `traceability`: `source_refs`, `invocations_in` / `invocations_out` (origen, destino, mecanismo, parámetros, **archivo y línea**, estado, refs), `usage_reasons` (con base y refs), `markup_controls`, `ui` (fidelidad y reporte de estilos). Las afirmaciones de IA siguen con `source_refs` y `basis`; `explanation.usage_reasoning` incluido.
* `ai/flows.json` — pasos de cada ruta con `source_refs` (y la etiqueta completa con el ID de apoyo).
* `ai/provenance.json` — proveedor, modelo, solicitudes, línea base y huellas, **`measurements`**, **`selection_criteria`**, **`module_evidence`**, puntero a `internal/behavioral/validation_report.json` y la política humano/IA.
* `internal/behavioral/` — `validation_report.json` (afirmaciones rechazadas y su motivo), `AI_INTERPRETATION_MANIFEST.json`, `ai_raw_responses.json`, `explanations.json`, `wireframe_models.json`, `ui_navigation_evidence.json`, `style_reconstruction_report.json`; `internal/baseline_reference.json`.
Otra IA puede responder: de dónde sale un hecho (`source_refs`), qué artefacto lo respalda (`file`/`line` de invocaciones, pasos de ruta), qué Evidence lo sustenta, qué afirmaciones se rechazaron (`validation_report.json`) y qué estado de validación existe.

## 3. Colores de estado
Al inicio del documento, **una sola vez**, tres tarjetas de leyenda: **Confirmado** (azul, borde sólido), **Inferido** (naranja, borde discontinuo), **No resuelto** (rojo, borde punteado), con una línea de significado cada una (el color nunca es la única señal: lleva texto y patrón de borde). Después, las afirmaciones se muestran como **tarjetas del mismo color**, agrupadas por estado, lo confirmado primero y la incertidumbre agrupada; no se repite la definición. Las tablas se conservan donde comunican listas estructuradas (proyectos y capa, catálogo, datos).

## 4. Aviso de IA
Un único aviso al inicio: **«Interpretación asistida por IA»** — «Este documento presenta una interpretación generada por IA a partir del análisis de IST. Las afirmaciones conservan su estado de confianza: Confirmado, Inferido o No resuelto.» — más la frase de portada «La documentación se construyó a partir del análisis de IST y de una interpretación de IA validada contra la evidencia disponible.». Desaparece la insignia morada «IA» de cada bloque: el texto de IA se muestra como prosa con una línea tenue y conserva `data-status="AI_INTERPRETATION"` en el marcado y el estado en el modelo. Si no hubo corrida de IA, el aviso lo dice.

## 5. Rutas técnicas
Se conservan íntegras (tabla «Acción | Ruta», «Ruta técnica detallada», flujos de cajas, invocaciones, datos/procedimientos), p. ej. en `ucPreMantJerarquia2`: `hypAsignar.Click → hypAsignar_Click → PreGesJerarquia.txcrear → sysPreGesJerarquia.crear → PPRE_GES_JERARQUIA.crear` (verificado en el HTML real). Solo se elimina el ID de apoyo `(DAO-…)` del nombre del paso (la etiqueta completa sigue en `ai/flows.json`). Prueba: `TechnicalRoutesRemain` en el test nuevo.

## 6. Verificación sobre la corrida real (sin volver a analizar)
Paquete nuevo generado desde el baseline y las respuestas de IA persistidos de `manual_final` (la corrida original **no se modificó**). Escaneo de `human/` (HTML guía y ejecutivo, SVG, PDF): **0** apariciones de `EP-`, `FLOW-`, `CALL-`, `DAO-`, `src:`, «Base de las afirmaciones», huella, `copilot-local`, `gpt-`. Antes (guía HTML): EP- 55, FLOW- 47, src: 71, DAO- 42, «Base de las afirmaciones» 3, «Afirmación» 28, insignias «IA» 6, 67 bloques `<details>`; ahora 38 `<details>` plegados, solo rutas técnicas y detalle de afirmaciones/limitaciones sin referencias. `verify.py package` (60 archivos con hash) y `ai-knowledge` (121 vistas): OK. `ai/knowledge.json`: 5 vistas detalladas con `traceability` (79 refs, 27 invocaciones con archivo:línea).

## 7. Llamadas y lecturas
* Llamadas al proveedor: **0** (las respuestas guardadas se re-validan con `ReplayProvider`).
* Escáner / analizador / Evidence: **no ejecutados**.
* Lectura del código fuente: **ninguna**.
* Semántica de IA: sin cambios de modelo, estados ni Evidence; el modelo de `ai/knowledge.json` solo **añade** `traceability` y claves de `provenance.json`.

## 8. Pruebas
* Nuevas: `tests/test_post_v5_h4_evidence_separation.py` (19): sin EP/FLOW/CALL/DAO/src/«Base…»/huella/proveedor en HTML y PDF (guía y ejecutivo) ni en SVG, sin «Línea», sin repetición de afirmación/base, un único aviso de IA y sin insignias repetidas, leyenda una sola vez antes de la sección 1, estados distintos (note/semantic/unresolved), tarjetas con lo conocido primero, rutas técnicas presentes en HTML y PDF, trazabilidad intacta en `ai/knowledge.json`, `flows.json` y `provenance.json`, modelo/Evidence sin cambios por la renderización, paquete sin llamadas al proveedor ni al pipeline.
* Ajustadas (comportamiento anterior fijado a propósito): `test_post_v5_h4_r4_behavioral`, `…_r5_behavioral_ai`, `…_content_polish`, `…_noise_pdf_polish`, `…_template_productization` (aserciones sobre insignia «IA», aviso largo, bloques de respaldo / diagnóstico, frase de procedencia).
* Selectivas H4 (8 archivos): OK.
* Suite completa `python -X utf8 -m unittest discover -s tests`: ejecutada una vez con los cambios estables: **3519 tests, 132 skips, 1018 s**; un único fallo, `test_on_disk_inventory_matches_fresh_build_if_present` (el inventario fijado en `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json` no incluía los módulos/tests nuevos). Se regeneró la clave `inventory` de ese archivo (igual que en la ronda anterior) y el módulo `test_v4_1_r0_maintainability_inventory` se volvió a ejecutar: 22 tests, OK. **No se repitió la suite completa tras ese ajuste**; el resultado es por tanto 0 fallos en la corrida completa salvo ese pin, ya corregido y verificado por separado.

## 9. Entorno de validación y ruta de revisión
La rueda reconstruida se instaló en `C:\PruebasLegacyMapper\FinalValidation\venv` (`runtime\wheel\…whl` actualizada). **Revisión:** `C:\PruebasLegacyMapper\FinalValidation\runs\manual_final_clean_human\package\` — abrir `human\index.html`, `human\LegacyMapper.pdf`, `human\executive.pdf`; lista de archivos en `runs\manual_final_clean_human\REVIEW_FILES.txt`. No se tocó `runs\manual_final`.

## 10. Estado
`H4_FINAL_HUMAN_INTERPRETATION_EVIDENCE_SEPARATION = READY_FOR_HUMAN_APPROVAL` · `H4 = HUMAN_APPROVAL_PENDING` · `H5 = NOT_STARTED`. El propietario inspecciona el paquete limpio; no se cierra H4 automáticamente.
