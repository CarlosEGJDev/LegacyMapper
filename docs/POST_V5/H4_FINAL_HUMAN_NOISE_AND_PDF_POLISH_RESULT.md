# H4 — Final Human Noise and PDF Polish: resultado

Estado: **`H4_FINAL_HUMAN_NOISE_AND_PDF_POLISH = READY_FOR_MANUAL_VALIDATION`**. **H4 = HUMAN_APPROVAL_PENDING** (no cerrado). **H5 = NOT_STARTED**. Sin commit, push ni tag.

## 1. Secciones humanas que cambiaron
Solo presentación: `behavior/render.py`, `behavior/prototype.py` (metadatos de portada PDF), `deliver/pdf.py`, `templates/human/executive/template.yaml`.

* **Ejecutivo:** «Lo que no se puede afirmar» y la tabla «Acciones cuyo destino posterior es indeterminado» desaparecen. Queda una sección final corta **«Limitaciones conocidas»** (1–4 viñetas, sin tablas ni nombres de llamadas) después del detalle por capacidad. El catálogo de 121 vistas pasa a un bloque plegado (HTML), la trazabilidad de IA es una línea sin proveedor/modelo y la portada del PDF ya no lleva huella ni nombres de proveedor.
* **Guía por defecto:** «Limitaciones conocidas» conserva el límite general y deja tabla de acciones indeterminadas, afirmaciones no resueltas y destinos inexistentes en bloques **plegados** (HTML completo, fuera del PDF). Por vista: el razonamiento de uso de la IA pasa al bloque plegado «Base del uso observable»; la parte «Qué sabemos, qué inferimos y qué no sabemos» pasa a «Trazabilidad de la vista», íntegramente plegada. El catálogo del apéndice dice qué parece hacer cada vista sin repetir «no resuelto / propósito no determinado» (121 filas).
* Orden por vista (sin cambios): frase → qué hace → uso → reconstrucción → flujo → **acciones (ruta)** → datos → relaciones → mensajes → trazabilidad plegada.

## 2. Incertidumbre quitada / plegada
Texto visible, antes → después (frases de incertidumbre: «no resuelto», «indeterminado», «no se puede/determina/especifica/conoce»): guía 330 → 104; ejecutivo 189 → 14. Caracteres visibles: guía 74 843 → 58 749; ejecutivo 38 363 → 18 795. PDF: guía 59 → 44 páginas; ejecutivo 15 → 9. Nada se elimina de la verdad: todo sigue en el modelo semántico, en `internal/` y en `ai/unresolved.json`.

## 3. Qué permanece en ai/ e internal/
`ai/` (7 archivos) **byte-idéntico** al de la ronda anterior (verificado con `cmp`); detalle completo de llamadas sin destino en `ai/unresolved.json` y `ai/flows.json`. `internal/behavioral/` conserva `explanations.json`, validación, manifiestos y respuestas crudas.

## 4. Cambios de paginación PDF y estrategia de wireframes
* **Reconstrucciones:** nueva estrategia en `deliver/pdf.py` (`_wireframe_pages`): (1) escalar el wireframe completo a **una página vertical** si la escala queda ≥ 0,5; (2) si es más alto, cortar **solo entre controles/grupos** (`_safe_cuts`: ningún corte atraviesa un botón, icono, etiqueta o fila; los contenedores grandes no se protegen, los hijos sí), todas las partes a la misma escala y con título «parte i de n»; (3) si no hay frontera lógica, se usa el cortador genérico previo. Las 5 vistas representativas caben en **una página cada una** (págs. 6, 11, 17, 23, 32 del PDF); ya no hay fragmentos verticales aislados (`iconoAsignar`, `iconoDesasociar`).
* **Reglas generales:** un subtítulo nunca queda solo al final de una página (reserva mínima de espacio y descarte de subtítulos cuyo contenido se omitió en el PDF); encabezado + leyenda de una figura se omiten porque la página de la figura lleva su propio título y aviso; las tablas no empiezan con encabezado + una fila (se mantienen juntas las primeras filas y las tablas cortas completas); sin marcas de tiempo; salida determinista.

## 5. Proveedor, escáner/analizador, fuente
Llamadas al proveedor: **0** (se re-valida la interpretación guardada de la ronda anterior, `copilot-local` / `gpt-6-luna`, 6/6). Escáner/analizador/Evidence: **no ejecutados**; fuente: **no leída** (pruebas con `run_full_pipeline` y registro de proveedores parcheados para fallar).

## 6. Pruebas
Nuevas: `tests/test_post_v5_h4_noise_pdf_polish.py` (13): ejecutivo sin tabla de llamadas y limitaciones ≤ 4 viñetas, sin nombres técnicos, detalle indeterminado plegado en la guía, sin repetición de la misma incertidumbre, conocido antes que incierto, razonamiento de uso plegado, `ai/` independiente de la presentación, sin proveedor/escáner, wireframe en una página, cortes solo entre controles, determinismo del PDF, subtítulo huérfano descartado. Ajustadas: Gate C (el ejecutivo ya no repite todas las afirmaciones no resueltas; permanecen en el modelo compartido) y R4 (título de la parte de trazabilidad). Dirigidas: 111 tests OK.

## 7. Suite completa
`python -X utf8 -m unittest discover -s tests`, ejecutada **una vez** con los cambios estables: **3494 tests, 0 failures, 0 errors, 132 skips, 800 s**. (Antes se regeneró la clave `inventory` de `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json` por el cambio de tamaño de los módulos.)

## 8. Ruta de revisión
`C:\PruebasLegacyMapper\Resultados\h4_final_human_noise_pdf_polish\package\` — abrir `human\index.html`, `human\LegacyMapper.pdf`, `human\executive.pdf`.

## 9. Limitaciones
PDF verificado por estructura (páginas, texto por página, cortes calculados), no con un visor ráster; los wireframes más altos (~1 300 unidades) se imprimen a escala ≈ 0,51 (texto pequeño pero íntegro; la guía HTML los ofrece a tamaño completo). El PDF ejecutivo/guía no incluye los bloques plegados por diseño.

## 10. Estado
`H4_FINAL_HUMAN_NOISE_AND_PDF_POLISH = READY_FOR_MANUAL_VALIDATION` · `H4 = HUMAN_APPROVAL_PENDING` · `H5 = NOT_STARTED`. Siguiente paso: corrida manual como usuario final con el contrato de paquete final.
