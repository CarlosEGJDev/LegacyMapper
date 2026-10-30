# Pre-H5 Gate B — UI / navegación / estilos en Evidence Core y semántica «analizar una vez»

**Estado: `PRE_H5_GATE_B_EVIDENCE_CORE = PASS`.** `PRE_H5_GATE_A_PORTABILITY = PASS` y `PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS` se mantienen. H5 = `NOT_STARTED`. Gate C no iniciado. Sin commit, push ni tag.

## 1. Alcance
Resuelve DT-03 (UI/navegación/estilos → Evidence Core) y evalúa la procedencia física vs. lógica. No toca DT-04, DT-07, DT-08, UX-03 ni V6.

## 2. Esquema (aditivo)
* `evidence_schema_version` **no cambia** (`1.0`): las particiones Core y `index/` quedan byte-idénticas (probado en IST: 0 particiones Core distintas).
* Nuevo `ui_evidence_schema_version = 1.0` en `EVIDENCE_MANIFEST.json` (+ bloque `ui_evidence` con extractor y autoridad).
* Ocho particiones nuevas, hasheadas por el manifiesto (la validación existente de la línea base las verifica sin cambios):

| Partición | Entidad | Contenido |
|---|---|---|
| `ui_documents` | UiDocument | `.aspx/.ascx/.master`: esqueleto tabla/fila/celda, code-behind, subs, imports, maestra, controles registrados/cargados, **anfitriones** (`SINGLE`/`AMBIGUOUS`/`NONE`), menciones de nombre entre vistas del proyecto, conteo de líneas |
| `ui_controls` | UiControl | tipo, id, etiqueta, atributos, columnas, `bound_to`, contenedor (tabla/fila/celda), validador→control, eventos servidor |
| `ui_event_bindings` | UiEventBinding | cláusulas `Handles` y atributos `OnXxx` (definido / no definido) |
| `ui_navigation` | UiNavigationEdge | invocaciones `url=carpeta/vista` (mecanismo, parámetros, `CONFIRMED`/`INFERRED`/`UNRESOLVED`, candidatos) + `uses_master`, `hosts_user_control`, `loads_user_control` |
| `ui_messages` | UiMessage | literal / dinámico (`text_kind`), mensajes de validadores |
| `ui_parameters` | UiParameter | `QueryString`, `parametrosURL`, claves `Session` |
| `ui_style_references` | UiStyleReference | hojas enlazadas (+ reglas estáticas por archivo), clases, estilo en línea, tema, referencias de estilo por control |
| `ui_assets` | UiAssetReference | imagen resuelta/no resuelta, razón, sha256; bytes base64 solo ≤ 16 KB |

Cada registro: `id`, `kind`, `logical_source_path`, `source_refs` (resuelven a `SRC-`), `status`, `properties`, `relationships`. Ids `UID-/UIC-/UIE-/UIN-/UIM-/UIP-/UIS-/UIA-` = SHA-256 de (id lógico de repositorio si se declaró, ruta relativa, tipo, id de control, ordinal de duplicado); sin ruta física, cwd ni usuario. Invariantes `UI-1..UI-5` en `validate_evidence` (fallan el análisis, no se persiste).

## 3. Extractores y capas
* Extracción **solo** en el adaptador: `adapters/vbnet_webforms_oracle/ui_extraction.py` (corre dentro de `NormalizedEvidenceBuilder`, es decir en el análisis; no toca la caché de extracción). Un markup mal formado queda registrado (`extraction_error`, `UNRESOLVED`), no aborta.
* Neutrales: `evidence/ui_model.py`, `evidence/ui_css.py`. Lector downstream: `behavior/ui_evidence.py` (verifica hash de cada partición).
* `behavior/source.py` ya no analiza ni lee archivos; `behavior/styles.py` ya no descubre ni abre disco (`StyleCatalog.from_evidence`); `BehaviorContext` perdió `repo_root`; `build(baseline, repo=None, …)` ignora `repo` (compatibilidad **explícita y temporal**); `--source` del prototipo es opcional y se ignora.
* `usage`: las menciones de nombre vienen de `UiDocument.mentions_views` (antes releía el texto de cada vista).
* Contexto de IA: parte del mismo `view_context`; añade hechos acotados `host_chain`, `master_page`, `assets`, `styles` desde la evidencia persistida.

## 4. Sidecar
`ui_navigation_evidence.json` pasa a **proyección derivada** (`authoritative: false`, `role: derived_projection`, `contract_version 2.0`), regenerable desde `evidence/ui_*.json`; nada lo lee como entrada. Sus hashes de fuente salen de `source_artifacts`.

## 5. Procedencia física vs. lógica
`scan_summary.root` / `source_repository` **no se reescribieron** (contrato histórico V5.9-R2). Se añade al manifiesto `source_provenance` (proyección derivada): `logical_source_id`, `logical_snapshot_sha256` (ruta+sha256 de cada archivo), `portable_evidence_sha256` (todas las particiones salvo `scan_summary`) y `physical_root` marcado `compatibility_metadata_not_identity`. Probado: misma fuente en dos ubicaciones → particiones `ui_*` y `source_provenance` byte-idénticos y ninguna ruta física dentro de ellas. Observación: `source_snapshot_sha256` de `SYSTEM_CONTEXT.json` es una constante literal heredada; no se modificó (deuda).

## 6. Compatibilidad
Línea base anterior (sin `ui_*`): H1/H2/H3/H4-deliver siguen válidas; el documento conductual falla explícito `UI_EVIDENCE_MISSING` (exit 4, JSON con acción «re-ejecutar analyze/full una vez»), `UI_EVIDENCE_SCHEMA_UNSUPPORTED` o `UI_EVIDENCE_PARTITION_CORRUPT`. **Nunca** se reinterpreta ni se lee la fuente como respaldo. `ANALYZER_VERSION` sigue en 3 (salida de análisis y Core byte-idénticos; precedente V5.9-R1); cambió la huella de código (test guardián actualizado).

## 7. Pruebas
* Dirigidas: `tests/test_post_v5_gate_b_ui_evidence_core.py` — **30 pruebas**: persistencia de controles/contenedores/eventos/navegación/mensajes/parámetros/estilos/activos/cadena maestra-anfitrión, no resueltos y anfitrión ambiguo preservados, paridad exacta con el parser directo, ids y particiones idénticos entre ubicaciones, fuente renombrada → behavior/docs/visuals/deliver/interpret OK con 0 lecturas, 0 scanner/analyzer/proveedor, baseline antiguo/versión/hash alterado, invariantes y fronteras de arquitectura (AST).
* Actualizadas por traslado del parser: `test_post_v5_h4_r4_behavioral`, `test_post_v5_h4_template_productization`; inventario (329 módulos) y huella guardián.
* Suite completa sobre el árbol final: `python -X utf8 -m unittest discover -s tests` → **3 413 pruebas, 0 fallos, 0 errores, 132 omitidos (históricos), exit 0, 857.9 s**. Historia honesta: la primera corrida dio 1 fallo (un segundo pin de la huella del analizador en `test_v5_8_r1_consumer_plugin_contract`); se corrigió y la suite completa se repitió; solo la segunda es la validación.

## 8. IST real (una sola corrida determinista)
| Medida | Resultado |
|---|---|
| Análisis completo | 1 scanner, 1 analyzer, SUCCESS, 11 min 35 s, 15 138 archivos |
| Particiones Core vs. línea base anterior | **0 distintas** |
| Nuevas | `ui_documents` 3 346 · `ui_controls` 90 707 · `ui_event_bindings` 12 620 · `ui_navigation` 2 221 · `ui_messages` 14 760 · `ui_parameters` 16 328 · `ui_style_references` 78 565 · `ui_assets` 6 678 (≈175 MB) |
| Estados de invocaciones | 1 055 CONFIRMED · 1 099 INFERRED (varias copias de la vista) · 32 UNRESOLVED |
| Downstream con fuente instrumentada (hook de auditoría `open`) | conductual (`--ai-replay`), `docs`, `visuals`, `deliver`: exit 0, **0 aperturas bajo la raíz de IST**, scanner 0, analyzer 0, proveedor 0 |
| Paridad | sidecar derivado = sidecar leído de fuente en las 121 vistas; menciones persistidas = algoritmo histórico (74/74, 0 diferencias); `wireframe_models` comunes idénticos |

La carpeta de la fuente IST **no se renombró** (es el árbol de trabajo del usuario); la prueba equivalente física está en las pruebas dirigidas (fixture renombrado) y en IST por el hook de auditoría.
Observación honesta: frente al paquete conductual del 13-oct, `usage_summary` pasa de `{ACTIVE 7, UNRESOLVED 114}` a `{ACTIVE 7, POSSIBLY_ACTIVE 52, UNRESOLVED 62}`. El algoritmo de menciones re-ejecutado hoy directamente sobre la fuente da el mismo resultado que la evidencia persistida (0 diferencias), por lo que la diferencia no proviene de este Gate; el paquete anterior no se pudo reproducir con este código. Queda para revisión humana.

## 9. Deuda restante (no resuelta aquí)
* Gate C: DT-04, DT-07, DT-08, UX-03.
* `ImageUrl="~/…"` no se resuelve contra la raíz de la app (2 727 activos sin resolver en IST); se mantuvo la semántica previa.
* Menú/configuración → vista no se extrae (no había evidencia previa).
* Tamaño: ≈175 MB adicionales en IST; reducible deduplicando atributos.
* `scan_summary.root` sigue físico; `source_snapshot_sha256` constante heredada.
