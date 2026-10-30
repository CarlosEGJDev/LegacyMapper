# H4 — Cleanup and Final Human Candidate: resultado

Estado: **`H4_CLEANUP_AND_FINAL_HUMAN_CANDIDATE = READY_FOR_OWNER_APPROVAL`** · **H4 = HUMAN_APPROVAL_PENDING** (no cerrado) · **H5 = NOT_STARTED**. Sin commit, push ni tag.

Revisión del propietario (únicamente estos tres archivos; también listados en `CURRENT_RUN.txt`):

```text
C:\PruebasLegacyMapper\FinalValidation\runs\final_h4_review\package\human\index.html
C:\PruebasLegacyMapper\FinalValidation\runs\final_h4_review\package\human\LegacyMapper.pdf
C:\PruebasLegacyMapper\FinalValidation\runs\final_h4_review\package\human\executive.pdf
```

## 1. Resumen de limpieza (Fase A)

Antes de borrar se comparó SHA-256 archivo por archivo: el baseline (48 114 archivos, 3 704 639 067 bytes) y las respuestas IA (47 archivos) de `manual_final`, `manual_final_layout_polish` y `manual_final_h4_candidate` eran **idénticos** (0 diferencias). Se movió el estado de `manual_final` a `state\` (mismos conteos, bytes y hash después), se archivaron las respuestas IA de las carpetas obsoletas y solo entonces se borró. Detalle en `C:\PruebasLegacyMapper\FinalValidation\CLEANUP_INVENTORY_BEFORE.md` y `CLEANUP_REPORT.md`.

**Carpetas eliminadas**
* `FinalValidation\runs\`: `manual_final`, `manual_final_clean_human`, `manual_final_layout_polish`, `manual_final_h4_candidate`.
* `Resultados\`: `h4_final_catalog_wireframe_polish`, `h4_final_human_noise_pdf_polish`, `h4_final_knowledge_productization`, `post_v5_h4_behavioral_doc_prototype`, `post_v5_h4_final_content_polish`, `post_v5_h4_final_deliverables_review`, `post_v5_human_template_productization`.

**Retenido / migrado**
* Retenido en `FinalValidation\`: `venv\`, `runtime\wheel\` (reconstruida con el código de esta ronda y reinstalada en el venv; mismo nombre de archivo), `scripts\` (actualizados), `README_RUN_ME.md`, `RUN_LEGACYMAPPER.cmd`.
* Retenido en `Resultados\` (no son salida de H4): `h5_real_ist_validation`, gates pre-H5 (`post_v5_gate_b/b1/c`), `post_v5_h2_human_review`, `post_v5_h3_visual_review`, `prueba_01/02`, y todos los `v4_3_*`, `v5_1_*`, `v5_2_*`. Dos de ellos (`v4_3_rebaseline`, `v5_1_r2_evidence_build`) son fixtures referenciados por tests. **Criterio aplicado: solo se borraron salidas de revisión de iteraciones H4 superadas; no se borró historia de versiones cerradas ni el runtime de H5.**
* Migrado: baseline y respuestas IA activas (ver rutas abajo); respuestas IA de las 7 carpetas obsoletas archivadas (22 archivos).

**Ruta final del baseline:** `C:\PruebasLegacyMapper\FinalValidation\state\baseline\`
**Ruta final de respuestas IA:** `C:\PruebasLegacyMapper\FinalValidation\state\ai\behavioral\` (archivo histórico en `state\ai\_archive\`)

Estructura final: `venv\`, `runtime\`, `scripts\`, `state\{baseline,ai}`, `runs\final_h4_review\`, `README_RUN_ME.md`, `RUN_LEGACYMAPPER.cmd`, `CURRENT_RUN.txt`, más los informes de entorno/limpieza. `RUN_ALL.cmd` ya no ejecuta 01 ni 02: solo comprueba y reutiliza `state\`.

## 2. Limpieza human / evidence (Fase B)

El candidato anterior ya estaba prácticamente limpio de trazabilidad (IDs `EP-/FLOW-/CALL-/DAO-`, `src:`, "Base de las afirmaciones", "Evidencia técnica", columnas "Dónde/Línea", provider/modelo, fingerprints, badge IA repetido). Esta ronda corrigió lo que el escaneo del candidato todavía mostraba:

* **Nota IA única, con el texto del prompt:** «Este documento presenta una interpretación generada a partir del análisis de IST. Las afirmaciones se distinguen como Confirmadas, Inferidas o No resueltas.» Se eliminó la frase de procedencia repetida en la portada (HTML y PDF) cuando hubo IA. Sin provider/modelo/fingerprint en la portada humana.
* **Rutas de archivos fuente fuera de lo humano:** el subtítulo de cada capítulo ya no muestra `WebPREPrevencion\ucX.ascx`; `behavior/humanize.py` nombra las vistas sin la extensión `.ascx/.aspx` (también en celdas de código); los wireframes ya no incluyen la ruta del archivo en su cabecera ni en `<title>`.
* **Solo tres estados humanos** (Confirmado / Inferido / No resuelto) en la leyenda; `AI_INTERPRETATION` y `CANONICAL` no aparecen en texto visible (solo como atributo `data-status` invisible en el marcado y en `ai/`/`internal/`).
* **Lenguaje:** el escaneo no encuentra «La evidencia muestra/confirma/no…», «según la evidencia» ni «Evidencia de uso» en HTML ni PDF (reglas ya existentes de `humanize`).

Escaneo final (HTML guía + ejecutivo, PDF guía + ejecutivo): 0 ocurrencias de `EP-`, `FLOW-`, `CALL-`, `DAO-`, `src:`, "Base de las afirmaciones", "Respaldo de la interpretación", "Evidencia técnica", `copilot-local`, `gpt-6`, `AI_INTERPRETATION`, `CANONICAL`, `(línea`, "Dónde (archivo", fingerprint, `.vb`, `.aspx`, rutas `WebPREPrevencion\` o `C:\`; 1 nota IA por documento; 0 etiquetas «IA» aisladas.

**Excepción declarada:** `LegacyMapper.pdf` conserva 7 apariciones de `ucX.ascx` y los SVG `ucbussuc-invocaciones.svg` / `ucpreestadisticasaccidentes-invocaciones.svg` conservan 1–2, todas **dentro de los diagramas de invocaciones**, que el prompt declara aprobados y congelados (byte-idénticos al candidato anterior). Son nombres de archivo de vista, no rutas. No los modifiqué para no tocar un diagrama aprobado; si el propietario quiere quitarlos, es un cambio de una línea en ese diagrama.

**Trazabilidad intacta:** `ai/` e `internal/` conservan `EP-`/`FLOW-`/`CALL-`/`DAO-`, rutas `.ascx`, líneas, `provider_id`/`model_id` y estados `AI_INTERPRETATION`/`CANONICAL` (`ai/`: 1866/966/237/297 ocurrencias de EP/FLOW/CALL/DAO; `internal/`: 273/236/192/183).

## 3. Correcciones de reconstrucciones de vistas

La mayor parte (Criterio, Hasta, Asignar/Desasociar, símbolos sueltos, ancho mínimo por palabra) ya estaba resuelta por el micro-polish anterior; el render real lo confirmó. Lo que faltaba y se corrigió:

* **Bitmaps de «cara de botón» comprimidos a 16×16:** los botones Buscar/Asignar/Desasociar incrustaban un GIF de ≈110×20 (el botón legacy con su texto) forzado al hueco de icono de 16 px, produciendo un borrón ilegible junto a la etiqueta. `wireframe.is_glyph_icon` descarta imágenes con proporción > 1.6 (no son iconos); los iconos cuadrados (p. ej. la lupa de «Ayuda») se conservan. Cambió 5/5 wireframes.
* Etiqueta/cabecera sin ruta del archivo fuente (ver sección 2).

## 4. Páginas / renders inspeccionados

Render real (Edge headless → PNG) de los cinco SVG de `final_h4_review\package\human\guide\assets\`:

| Vista | Resultado |
|---|---|
| `ucPreMantJerarquia2` | «Asignar» / «Desasociar» como dos botones legibles y coherentes en columna central ancha; sin `<`/`>` sueltos, sin símbolos apilados, sin clipping ni solapes; `lblMensaje1/2` debajo de las acciones |
| `ucBusSuc` | «Criterio» horizontal y legible junto a la lista y la caja |
| `ucPreMantEmpadronamiento` | sin palabras verticales, sin solapes, controles dentro del marco |
| `ucPreEstadisticasAccidentes` | meses/etiquetas horizontales; sin borrón en «Buscar»; lupa de «Ayuda» conservada; sin controles fuera del marco |
| `ucPreConActxProd` | `[fec_ini]  Hasta  [fec_fin]` en una línea, «Hasta» horizontal; sin «Desde» inventado |

Estructural PASS (tests) y visual legible PASS (inspección de raster). Observaciones menores no corregidas, fuera del alcance pedido: en `ucPreEstadisticasAccidentes` y `ucPreMantEmpadronamiento` algunas cajas muestran el id recortado con «…» (`[txtContr…]`, `snt:…`) por el ancho de celda; es legible como reconstrucción documental pero no es ideal.

No inspeccioné el raster de las páginas del PDF: el PDF se verificó por extracción de texto (pypdf, sin rasterizar páginas) y por los tests; sí confirmé que los SVG incrustados son los inspeccionados.

## 5. Prueba de diagramas congelados

Comparación SHA-256 de los 33 activos no-wireframe de `human\guide\assets\` (flujos, rutas, dependencias, datos, invocaciones, mapas) contra el candidato anterior: **0 cambiados**. `human\diagrams\index.html` y `human\index.html`: idénticos. Solo cambiaron los 5 wireframes. (La comparación se hizo antes de borrar el candidato anterior.)

## 6. Contadores de la tarea

| | |
|---|---|
| Llamadas al provider | **0** (`provider_calls: 0` en el log del paso 3; no se ejecutó `02_INTERPRET_WITH_AI`) |
| Scanner / analyzer | **0** (no se ejecutó `01_ANALYZE_ONCE`) |
| Reconstrucción de Evidence | **0** |
| Lecturas de fuente | **0** (solo baseline y respuestas IA persistidas) |

Nota de transparencia: para esta ronda se reconstruyó la wheel desde el checkout (`pip wheel --no-deps`) y se reinstaló en el `venv` aislado para que la corrida final use el código corregido; no se modificó la lógica de análisis.

## 7. Tests

**Dirigidos** (221 tests de `test_post_v5_h4_*`: content_polish, evidence_separation, template_productization, layout_polish, screen_narrative, noise_pdf_polish, knowledge_productization, r4_behavioral, r5_behavioral_ai, deliver): OK. Tests nuevos/actualizados:
* `FinalCandidateIconRules` (`test_post_v5_h4_layout_polish.py`): cara de botón ancha no es icono / icono cuadrado sí; texto único de la nota IA en ambas plantillas; vistas nombradas sin `.ascx/.aspx` (prosa y código); wireframe sin ruta en cabecera ni `<title>`.
* Actualizados 4 tests que fijaban la frase de procedencia antigua en portada y el texto antiguo de la nota IA (`content_polish`, `evidence_separation`, `template_productization` ×2).
* Se actualizó la clave `inventory` de `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json`: el test `test_on_disk_inventory_matches_fresh_build_if_present` fija el conteo de líneas/funciones de los módulos vivos (`behavior/wireframe.py`, `behavior/humanize.py`) y falló en la primera suite completa al cambiar esos archivos. Es la única modificación a ese documento; el resto de claves no se tocó.

**Suite completa** (`python -X utf8 -m unittest discover -s tests`, una vez tras el ajuste del inventario): **3551 tests, OK, 0 failures, 0 errors, 132 skipped.** (La primera ejecución completa dio 1 fallo — el pin de inventario descrito arriba —, corregido antes de la ejecución final.)

## 8. Archivos tocados en el repositorio

`legacy_documenter/behavior/render.py`, `behavior/prototype.py`, `behavior/wireframe.py`, `behavior/humanize.py`, `templates/human/default/template.yaml`, `templates/human/executive/template.yaml`; tests: `test_post_v5_h4_layout_polish.py`, `..._content_polish.py`, `..._evidence_separation.py`, `..._template_productization.py`; `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json` (solo `inventory`). Fuera del repo: `C:\PruebasLegacyMapper\FinalValidation\` (scripts, README, state, runs, informes).

## 9. Siguiente paso

El propietario revisa los tres archivos de la ruta final. Si los aprueba, el siguiente paso es el cierre formal de H4. No se inició H5 ni se cerró H4.
