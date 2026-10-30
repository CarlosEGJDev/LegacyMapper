# Pre-H5 Gate B.1 — Cierre del Evidence Core (activos, navegación, procedencia, tamaño, paridad)

**Estado: `PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE = PASS`.** Gate A, A.1 y B siguen `PASS`. H5 = `NOT_STARTED`. Gate C no iniciado. Sin commit, push ni tag.

## 1. Resumen por ítem
| Ítem | Resultado |
|---|---|
| B1-01 activos `~/` | Resuelve contra la raíz de aplicación (directorio del proyecto que declara el documento). Una raíz → `CONFIRMED` solo si el archivo existe en la instantánea analizada; varias → `UNRESOLVED/AMBIGUOUS_APPLICATION_ROOT`; ninguna → `APPLICATION_ROOT_UNKNOWN`; inexistente → `ASSET_NOT_FOUND`. Se persiste `resolution_basis`, ruta lógica, sha256 y `source_refs`. |
| B1-02 menú/config → vista | Nuevo `menu_entry` en `ui_navigation` para literales `url=carpeta/vista` y rutas `.aspx/.ascx` en `.xml/.config/.sitemap`; objetivos dinámicos (`{0}`, `<%`, `$(`) → `UNRESOLVED/DYNAMIC_TARGET`; no se infiere por nombre de archivo. No altera la semántica de invocaciones ni de uso; llega al contexto de IA como hecho acotado. |
| B1-03 deriva de uso | Diagnóstico abajo (§3). |
| B1-04 procedencia portable | Identidad/hash de paquete usan `portable_evidence_sha256` + `logical_snapshot_sha256`; `evidence_manifest_sha256` (depende de `scan_summary.root`) sale de los artefactos portables conductuales y se conserva como diagnóstico en baselines sin `source_provenance`. HTML/JSON/SVG conductuales idénticos byte a byte entre dos raíces, sin rutas físicas. |
| B1-05 `source_snapshot_sha256` | Opción C: el campo histórico se conserva (era una constante literal; ahora declarado `source_snapshot_sha256_semantics = legacy_contract_constant_not_a_content_hash`) y se añaden `logical_snapshot_sha256` (ruta + sha256 de cada archivo) y `portable_evidence_sha256` en `SYSTEM_CONTEXT.json`, `BaselineInfo` y manifiestos de entrega. Misma fuente en dos raíces → mismo hash; un cambio de contenido → hash distinto. |
| B1-06 tamaño | UI Evidence en IST **174.7 MB → 108.0 MB (−38 %)**, determinista. `ui_style_references` 51 → 1 MB (perfiles de estilo compartidos: 78 398 registros por control → perfiles únicos), hijos sin repetir ruta/procedencia del documento. Sin pérdida semántica (paridad exacta con el parser directo). |
| B1-07 ciclo | `behavior.styles` ya no importa `ui_evidence`; la dirección es `ui_evidence → styles` (el catálogo recibe un `icon_resolver`). Prueba AST de grafo acíclico. |

Esquema `ui_evidence_schema_version` 1.0 → **1.1** (envolturas hijas sin `source_refs`/`logical_source_path`, `source_scope`, `style_profile`, `resolution_basis`, `menu_entry`). Core y `evidence_schema_version` (1.0) intactos. Una línea base de Gate B (UI 1.0) falla explícito `UI_EVIDENCE_SCHEMA_UNSUPPORTED`: requiere un re-análisis. Invariantes `UI-1..UI-5` ajustadas (el hijo resuelve su procedencia por `document_id` + `source_scope`).

## 2. IST real (una sola corrida determinista)
| Medida | Resultado |
|---|---|
| Análisis | 1 scanner, 1 analyzer, SUCCESS (~12 min), 15 138 archivos, 3 346/3 346 documentos extraídos, 0 ilegibles |
| Particiones Core vs. Gate B | **0 distintas** (`logical_snapshot_sha256` igual) |
| Activos `~/` | 43 literales: **20 `CONFIRMED`**, 15 `ASSET_NOT_FOUND`, 8 `APPLICATION_ROOT_UNKNOWN`; activos totales CONFIRMED 3 814 → 3 834 |
| Menú/config | `navigation.xml`: 87 `menu_entry` UNRESOLVED (`url=webUsuarios/ejemplo…` no existen: plantilla de ejemplo) · `Web.config`: 5 CONFIRMED |
| Invocaciones | 1 055 CONFIRMED · 1 099 INFERRED · 32 UNRESOLVED (sin cambio) |
| Tamaño UI Evidence | 174.7 MB → 108.0 MB |
| Uso | `{ACTIVE 7, POSSIBLY_ACTIVE 52, UNRESOLVED 62}` (estable respecto a Gate B) |
| Downstream fuente instrumentada | conductual (`--ai-replay`), `docs`, `visuals`, `deliver`: exit 0; **0 aperturas bajo la raíz IST**, scanner 0, analyzer 0, proveedor 0 |
| `portable_evidence_sha256` | `a7798cb5…` (independiente de la raíz física) |

Hallazgo honesto: el «2 727 activos sin resolver» de Gate B **no** era mayormente `~/`: solo hay 43 literales `~/`. Los ≈2 570 restantes son rutas relativas (`../img/…`) cuya base depende del contexto de ejecución (los controles se cargan desde páginas de otras carpetas; desde la raíz salen del repositorio). No se adivinan: permanecen `UNRESOLVED` (deuda de contexto de ejecución).

## 3. B1-03 — Diagnóstico de la deriva de uso
* Hechos: los paquetes del 12/13-oct (4 artefactos) registran `name_references = 0` en **todas** las vistas, incluso `ucBusSuc` con 25 invocaciones entrantes confirmadas. Es un estado imposible: una vista abierta por 25 literales `url=` en código de vistas del proyecto necesariamente aparece por nombre en ese código.
* Descartado C (instantánea cambiada): las particiones Core del análisis actual son idénticas a las de la línea base usada (`f12b2b56…`).
* Descartado D (fixture/proyección): misma línea base, mismo proyecto/solución.
* Verificación: el algoritmo histórico re-ejecutado hoy directamente sobre la fuente da referencias > 0 en 74 de 121 vistas, idéntico a la evidencia persistida (0 diferencias); la evidencia, además, es regenerada por la corrida B.1.
* Conclusión: **A/B — el paquete H4 era incorrecto en `name_references`** (la lectura de texto de esa corrida no aportó contenido; el código de entonces silenciaba errores de lectura con `except OSError: pass`). El estado de código exacto de aquella corrida no es recuperable (el directorio `behavior/` no estaba versionado), por lo que la causa mecánica concreta queda `UNRESOLVED_HISTORICAL_PARITY`; el diagnóstico de incorrección y la paridad actual sí están probados.
* Acciones: paquetes del 12/13-oct marcados **históricos/superseded** (este documento); la extracción ya no silencia lecturas fallidas (`extractor.summary.unreadable_documents` en el manifiesto) y una prueba de regresión exige `name_references ≥ 1` en toda vista con invocación confirmada.

## 4. Pruebas
* `tests/test_post_v5_gate_b1_evidence_core_closure.py` — **19 pruebas** (activos `~/` única/faltante/ambigua/sin raíz, menú/config literal/dinámico/ausente, paridad de uso, ilegibles reportados, mismo origen en dos raíces, cambio de contenido, semántica de snapshot, paquete conductual idéntico sin rutas físicas, hijos sin envoltura repetida, perfiles compartidos, determinismo, fuente removida, grafo acíclico).
* Gate B actualizado a esquema 1.1 (30 pruebas OK). Inventario (329 módulos) y las dos huellas guardianas actualizadas.
* Suite completa única sobre el árbol final: `python -X utf8 -m unittest discover -s tests` → **3 432 pruebas, 0 fallos, 0 errores, 132 omitidos (históricos), exit 0, 715.8 s**.

## 5. Deuda restante
* Gate C: DT-04, DT-07, DT-08, UX-03.
* Rutas relativas de activos dependientes del contexto de ejecución (≈2 570 en IST).
* `scan_summary.root`/`source_repository` siguen físicos (compatibilidad; ninguna lógica nueva los usa como identidad).
* Causa mecánica exacta del paquete H4 de uso: irrecuperable (`UNRESOLVED_HISTORICAL_PARITY`).
