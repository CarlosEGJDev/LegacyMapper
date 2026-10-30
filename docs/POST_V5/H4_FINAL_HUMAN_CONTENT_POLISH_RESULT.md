# H4 — Final Human Content Polish: resultado

Estado: **`H4_FINAL_HUMAN_CONTENT_POLISH = READY_FOR_HUMAN_APPROVAL`**. **H4 = HUMAN_APPROVAL_PENDING** (no cerrado). **H5 = NOT_STARTED**. Sin commit, push ni tag.

## 1. Qué cambió (solo capa de presentación y textos deterministas)
`legacy_documenter/behavior/render.py` y `legacy_documenter/behavior/explain.py`. Sin cambios en Evidence, analizador, adapters, proveedor, validación de IA, plantillas CSS/YAML.

* **Narrativa de IA sin andamiaje:** desaparecen «Basada en: …» y «Razonamiento: …» intercalados. Referencias y razonamiento siguen disponibles en un bloque plegado «Respaldo de la interpretación» al final de cada capítulo (HTML; no se imprime en PDF).
* **Acciones = tabla Acción → Ruta** con los símbolos reales (`btnBuscar.Click → btnBuscar_Click → PrePrevencion.txcrear → … → PPRE_X.CREAR`); sin saltos repetidos (`MyBase.Load`, `Clase.Manejador`, `(DAO-…)`); un extremo abierto se escribe una vez: `destino posterior indeterminado`.
* **Nombres y relaciones en lugar de conteos:** «La abren: A, B, C…» / «Abre: …», patrones de datos del proyecto con nombres de vistas por tipo de operación, uso observable agrupado con los nombres de las vistas, sin «(xN)», sin «N operación(es)», sin «Invocaciones (26)».
* **Incertidumbre agrupada:** la sección «Áreas no resueltas» declara una vez el límite general (propósito de negocio / textos en ejecución), más una tabla «Acciones cuyo destino posterior es indeterminado» (vista, acción, llamada) y los destinos de invocación inexistentes. En cada vista, una sola línea «Llamadas cuyo destino no se sigue…» (detalle plegado). Se eliminan las frases repetidas «Estado: no resuelto», «el análisis no encuentra…» y los avisos vacíos («No se detectaron mensajes…», «No se confirmó ninguna operación de datos…»); una parte sin contenido propio simplemente no se muestra.
* **Resumen técnico plegado:** tablas «Afirmación / Estado / Base», criterio de selección de vistas, fidelidad de la reconstrucción y tablas de invocaciones pasan a bloques plegados; la reconstrucción conserva el rótulo «NO ES UNA CAPTURA DE PRODUCCIÓN» en una línea.
* **Línea base (huella):** de la portada al apéndice técnico.

## 2. Qué se quitó de la narrativa humana y qué permanece interno
Quitado de la narrativa: conteos de llamadas/hechos/controles/afirmaciones, IDs de Evidence (FLOW/CALL/EP/DAO), razonamiento de IA intercalado, huella en portada, criterios de selección piloto, estados repetidos.
Permanece interno y sin cambios: `explanations.json` (modelo estructurado, todas las afirmaciones y estados), `validation_report.json`, `AI_INTERPRETATION_MANIFEST.json`, `ai_raw_responses.json` (contenido idéntico a la corrida real), Evidence y baseline. Las mediciones siguen en el apéndice técnico del documento por defecto.
Cambian solo 4 textos deterministas del modelo (sin cambiar estado ni referencias): resumen de la acción (nombres en lugar de «N operación(es)»), llamadas no resueltas (sin «xN»), patrones de datos del proyecto (nombres en lugar de conteos) y frase final de comportamiento del proyecto.

## 3. Diferencias por audiencia
| | Ejecutivo (`human/executive`) | Funcional/general (`human/default`) |
|---|---|---|
| Orden | solución → proyecto → capacidades → impacto en datos → lo que no se puede afirmar → detalle → apéndice mínimo | solución → proyecto → módulos → vistas → entre vistas → datos → uso → no resuelto → apéndice |
| Capítulo de vista | frase, qué hace, uso, acciones (solo lenguaje natural o lista de acciones) | + qué recibe, reconstrucción, flujo, tabla de rutas, datos, clases, relaciones, mensajes |
| Nombres técnicos | sin métodos, manejadores, clases, referencias, huellas ni respaldo | rutas con símbolos reales; respaldo plegado |
| Datos | por efecto → nombres de vistas | procedimiento / efecto / quién lo alcanza |
| Apéndice | catálogo reducido + una línea de trazabilidad | catálogo completo, mediciones, fidelidad, huella, plantilla |

No se creó una tercera plantilla «técnica»: el lector técnico usa las rutas y el apéndice de `human/default`.

## 4. IA, código fuente y análisis
* **Proveedor de IA: 0 llamadas** (re-validación de las 6 respuestas guardadas; `provider_calls: 0`).
* **Código fuente: no leído** durante el renderizado; **escáner/analizador/Evidence: no ejecutados**; baseline persistido sin cambios.
* Contenido de `ai_raw_responses.json` idéntico al de la corrida real; el manifiesto conserva proveedor `copilot-local`, modelo `gpt-6-luna` y las solicitudes originales (`original_requests`).

## 5. Limitación pendiente (requiere decisión)
El **texto generado por la IA** (p. ej. el resumen del proyecto) todavía contiene métricas («121 vistas», «26 sitios», «7 con uso observable, 52…»). No se modifica texto de IA de forma determinista ni se vuelve a llamar al proveedor. Para que esa prosa sea más corta y sin conteos hace falta una **nueva interpretación de IA** con instrucciones de estilo («simple, conciso, sin conteos del análisis»; en `behavior/ai.py` `SYSTEM`/`INSTRUCTION`). **No se llamó ni se modificó el prompt**; se deja a autorización explícita (cambiaría los `request_id` de procedencia).
Tampoco se implementó conocimiento de dominio confirmado por humanos (COB = Cobranza, etc.): no se inventó ningún mapeo; el mecanismo existente `CANONICAL`/revisión es el candidato y queda para una ronda autorizada.

## 6. Comparación antes/después (IST real, 5 vistas representativas)
Texto visible (sin plegados), `ucPreMantJerarquia2 / ucBusSuc / ucPreMantEmpadronamiento / ucPreEstadisticasAccidentes / ucPreConActxProd`:

| Vista | Caracteres antes → después | Menciones de incertidumbre | «Basada en/Razonamiento» | IDs de Evidence visibles |
|---|---|---|---|---|
| ucPreMantJerarquia2 | 12 341 → 6 838 | 14 → 4 | 24 → 0 | 30 → 0 |
| ucBusSuc | 10 342 → 5 707 | 10 → 3 | 20 → 0 | 14 → 0 |
| ucPreMantEmpadronamiento | 16 947 → 9 218 | 10 → 3 | 26 → 0 | 28 → 0 |
| ucPreEstadisticasAccidentes | 13 294 → 8 184 | 13 → 8 | 30 → 0 | 34 → 0 |
| ucPreConActxProd | 9 484 → 5 007 | 17 → 5 | 22 → 0 | 19 → 0 |

Documento completo (texto visible): por defecto 99 126 → 74 215 caracteres; ejecutivo 68 550 → 37 642. «Basada en/Razonamiento»: 62 → 0 (por defecto) y 48 → 0 (ejecutivo); IDs de Evidence visibles: 128 → 0 y 100 → 0; «(xN)»: 47 → 0 y 8 → 0.

## 7. Pruebas
* Nuevas: `tests/test_post_v5_h4_content_polish.py` (13): respaldo plegado, sin conteos, rutas con nombres reales sin saltos repetidos, extremo abierto único, incertidumbre agrupada y no repetida, no resuelto preservado en el modelo, ejecutivo sin internos, diferencias de audiencia, portada ejecutiva sin proveedor/modelo, diagnósticos disponibles en el modelo, sin proveedor ni lectura de archivos, plantillas no cambian el modelo, PDF omite el respaldo plegado.
* Ajustada: `tests/test_post_v5_h4_r4_behavioral.py` (la parte «Datos y persistencia» ya no se muestra vacía).
* Dirigidas (R4, R5, productización, Gate C, polish): 115 tests OK.
* Suite completa: ver §8.

## 8. Suite completa
Suite completa ejecutada **una vez**: `python -X utf8 -m unittest discover -s tests` → **3467 tests, 1 fallo, 132 skips, 821 s**. El único fallo fue el snapshot vivo del inventario (`test_on_disk_inventory_matches_fresh_build_if_present`: `render.py`/`explain.py` cambiaron de tamaño/hash); se regeneró la clave `inventory` de `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json` (sin cambiar el resto) y se re-ejecutaron inventario + Gate C (44 tests OK). No se reejecutó el análisis IST.

## 9. Ubicación de la revisión humana
`C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_content_polish\`
* `before\{default,executive}\` — `index.html`, PDF y `view_<vista>.html` de las 5 vistas (estado anterior).
* `after\{default,executive}\` — `index.html`, PDF, `view_<vista>.html`, `explanations.json`, `validation_report.json`, manifiestos.
* `view_metrics.json` — métricas por vista; `COMPARISON.md`.
Abrir `after\default\index.html`, `after\executive\index.html` y los PDF; los bloques plegados (`Respaldo de la interpretación`, `Base de las afirmaciones`…) se despliegan en HTML.

## 10. Estado
`H4_FINAL_HUMAN_CONTENT_POLISH = READY_FOR_HUMAN_APPROVAL` · `H4 = HUMAN_APPROVAL_PENDING` · `H5 = NOT_STARTED`. El cierre de H4 requiere aprobación explícita del propietario.
