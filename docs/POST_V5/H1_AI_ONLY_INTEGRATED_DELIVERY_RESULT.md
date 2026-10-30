# H1 — AI-only desde un baseline determinista existente: resultado

Estado final: **`H1_READY_FOR_HUMAN_REVIEW`**. Sin commit, push ni tag. No se inició H2.

Criterio de aceptación (demostrado): un usuario puede analizar un repositorio una vez, conservar el output determinista y más tarde ejecutar interpretación/propuestas de IA desde ese output **sin reescanear la fuente**, conservando provenance, grounding, compatibilidad de revisión y autoridad humana.

## 1. CLI elegida
`python main.py interpret <output-existente>` — encaja con los verbos del CLI (`analyze`, `full`, `review`, …) y es más corto que `interpret-existing`/`ai-only`. Recibe un **directorio de output**, no un repositorio. Opciones: `--output` (AI run dir, nuevo/vacío), `--profile {TINY,SMALL,MEDIUM,LARGE}` (def. SMALL), `--flow-id` (repetible), `--verify-evidence {hash,fast}` (def. hash). Sin opciones de provider nuevas: usa exactamente la resolución existente (`resolve_provider`). El `--help` declara que no reescanea, no reconstruye Evidence, exige baseline válido, refiere `AI_ONLY_INPUT_INVALID` antes de cualquier llamada y que nunca es canónico (test lo verifica).

## 2. Inventario empírico del output persistido (verificado en código y en un output real)
* **Evidence:** `evidence/*.json` + `EVIDENCE_MANIFEST.json` (`evidence_schema_version`, `entity_counts`, `partition_sha256`, `repository_id` si se declaró).
* **Entrada real de la IA:** `index/*.json` (hidratación de flujos) + `ai_context/SYSTEM_CONTEXT.json` (`source_snapshot_sha256`). `run_ai_interpretation` **ya** leía solo esos archivos: la etapa de IA es reutilizable tal cual.
* **Identidad/versión:** `ai_context/SYSTEM_CONTEXT.json` (repositorio, snapshot), `_cache_v53/CACHE_MANIFEST.json` (analyzer version/fingerprint, `root_fingerprint`; **ausente** si el cache estuvo off o en outputs de `analyze`), `RUN_SUMMARY.json` (solo `full`).
* **Supuestos de estado en memoria:** ninguno bloqueante; `run_ai_interpretation` no usa objetos del análisis. Lo único que escribía junto con `full` eran `proposals/` en el mismo directorio.
* **Re-escaneo accidental:** ninguno en la etapa de IA; la guarda de tests lo prueba parcheando scanner/extractor/resolvers/`run_full_pipeline`/`analyze_repository`.
* **Output real usado:** `C:\PruebasLegacyMapper\V5_USER_ACCEPTANCE\outputs\IST_REAL_AI` (IST completo ejecutado por el usuario en el clean-room; etapas determinísticas todas SUCCESS, la etapa de IA de esa corrida falló con `PROVIDER_ERROR`). No se re-ejecutó IST.

## 3. Cambios de arquitectura (mínimos)
* Nuevo `legacy_documenter/orchestration/ai_only.py`: `validate_baseline` (puerta) y `run_ai_only` (puerta → aislamiento de output → etapa de IA **sin cambios** → `proposal_adapter` **sin cambios** → mismo escritor de propuestas que `full`).
* Nuevo `legacy_documenter/cli/interpret_command.py` (adaptador delgado) y registro en `parser.py`/`router.py`/`main.py`; clasificación de las opciones nuevas en `fingerprints/configuration.py`.
* **Aislamiento y compatibilidad con revisión:** AI run dir = `<baseline>/ai_runs/<run-id>/` (o `--output`) con `proposals/`, `AI_RUN_PROVENANCE.json` e `index/` de **hard links** al baseline (copia si no es posible). Así el flujo V5.7 funciona **sin modificarlo**: `review list|prepare|decide|canonical --output <ai-run-dir>`, y un cambio posterior del índice del baseline se detecta como obsoleto (stale). El baseline no se modifica ni recibe `knowledge/`.
* Sin cambios en el fingerprint del analyzer (`f05b2de4…`, v3), esquemas, contratos V5 ni review.

## 4. Puerta de validación (antes de cualquier provider)
Directorio existe; si hay `RUN_SUMMARY.json`, las 9 etapas deterministas son SUCCESS; `EVIDENCE_MANIFEST.json` presente y válido; schema soportado (`1.0`); cada partición presente y, con `--verify-evidence hash`, su SHA-256 coincide con el manifest; índices requeridos presentes; `ai_context` requerido presente y legible con identidad de fuente (`source_snapshot_sha256`); conteo de `source_artifacts` coherente con el manifest; `analyzer_version` (si consta) igual al actual; fingerprint actual comparado y registrado (`fingerprint_matches_current`, `null` si desconocido). Fallo → `AI_ONLY_INPUT_INVALID` + razón, exit 4, **0 llamadas a provider** (se cierra el provider inyectado; no se resuelve ninguno). Reutiliza las constantes/contratos existentes (`EVIDENCE_SCHEMA_VERSION`, `EVIDENCE_MANIFEST_FILENAME`, `analyzer_code_fingerprint`, `ANALYZER_VERSION`); no existía un verificador de manifest persistido que reutilizar, así que la verificación de hash de particiones es nueva y mínima.

## 5. Pruebas (todas con Fake grounded, sin red)
`tests/test_post_v5_h1_ai_only.py` — 24 tests: baseline válido; output inexistente; manifest ausente/ inválido; partición ausente/corrupta; schema y analyzer no soportados; AI context ausente; identidad de fuente ausente; índice ausente; etapa determinista fallida; output no vacío; **provider nunca llamado ni resuelto ante baseline inválido**; **ningún scanner/extractor/resolver/pipeline ni `analyze_repository` invocado**; **funciona con el árbol fuente eliminado**; propuesta grounded `READY_FOR_REVIEW`, no canónica, provenance completa; baseline idéntico antes/después (hash por archivo, y byte-idéntico con `--output` externo); revisión (`review list`, `prepare`, `decide APPROVE` humano explícito → canónico solo en el AI run dir); CLI help, exit 4/0, y un repositorio fuente pasado por error es rechazado (no analizado).
Ajustes de tests existentes por el cambio (esperados): conteo de módulos de producción 290→292; snapshot vivo de inventario → `docs/POST_V5/H1_AI_ONLY_INVENTORY.json`; clasificación de opciones del CLI; `ai_only.py` autorizado como consumidor de `versions`/`fingerprints`.
* Dirigidos H1 + inventario + fingerprints: 101 tests OK.
* **Suite completa: 3124 tests, 0 failures, 0 errors, 132 skips (854 s).** (3100 + 24 nuevos.)

## 6. Validación real
**Pequeña** (`v4_2_r7_full_sample`, copiado): `full` → baseline; fuente eliminada; `interpret` → SUCCESS, 1 propuesta, baseline sin cambios.
**IST** (`IST_REAL_AI`: 15 138 source artifacts, 12 642 flujos, 170 020 paths; 47 529 archivos / 2 828 160 172 bytes): validación `--verify-evidence hash` 7.5 s (fast 0.3 s); interpretación (carga de ~951 MB de índice + selección + paquete SMALL + 1 request Fake) 17.0 s; **total AI-only ≈ 17 s** con `fast`; contextos considerados: 1 paquete (perfil SMALL, selección acotada); llamadas a provider: 1 (Fake) / reales 0; propuestas: 1; scanner/extractor/`full`: **0 invocaciones**; delta del baseline: **0 añadidos, 0 eliminados, 0 cambiados** (tamaño+mtime de 47 529 archivos); `index_link_mode = hardlink`, `canonical=false`.
**Comparación de costo:** análisis determinista completo de IST (histórico, V5.9 R2 cold): ~652–657 s; AI-only: ~25 s (hash) / ~17 s (fast) de carga + preparación + validación.

## 7. Limitaciones conocidas
* La carga de todos los `index/*.json` (≈951 MB en IST) domina los ~17 s y la memoria; es el diseño existente de `run_ai_interpretation`, no se optimizó (fuera de alcance).
* La prueba con **provider real no se ejecutó** (no se documentó un camino manual seguro nuevo para H1; el uso real es `interpret` con la configuración existente del provider y requiere decisión explícita). Un `interpret` sobre IST con el provider real aún no está validado: la corrida real previa del usuario sobre `IST_REAL_AI` terminó en `PROVIDER_ERROR`.
* Un output sin `_cache_v53/CACHE_MANIFEST.json` (cache off, `analyze`) no trae analyzer version/fingerprint: se registra `origin=unknown`, no se rechaza.
* La resolución completa de todas las referencias de provenance no se repite en la puerta (sería re-validar Evidence); se cubre con hash de particiones + conteo + validación de refs por hallazgo + grounding de `review`.
* Sin sellado criptográfico del AI run dir; hard links comparten inodo con el baseline (si se edita un índice en sitio, ambos cambian y `review` lo ve como stale).
* `interpret` sobre un baseline cuyo `index/` esté hecho de un analyzer más viejo → rechazo (`ANALYZER_VERSION_UNSUPPORTED`) cuando el cache manifest lo declara.

## 8. Deuda introducida
Ninguna bloqueante. Observaciones: verificación de hash recorre ~1 GB de Evidence (7.5 s en IST; `--verify-evidence fast` existe); UX-01 (`full` con repo inexistente) sigue abierta; evaluar a futuro un `interpret` que reutilice solo los índices necesarios para bajar memoria.

## 9. Estado Git
Cambios sin commitear: `legacy_documenter/orchestration/ai_only.py`, `legacy_documenter/cli/{interpret_command,parser,router}.py`, `legacy_documenter/{main,fingerprints/configuration}.py`, `tests/test_post_v5_h1_ai_only.py`, dos tests existentes ajustados (`test_v4_1_r0_maintainability_inventory.py`, `test_v5_3_r2_3_versioning_and_fingerprints.py`), `README.md`, `docs/V5/V5_OPERATIONS_GUIDE.md` (§11), el roadmap post-V5, `PROJECT_STATE.json`, `docs/POST_V5/H1_AI_ONLY_INVENTORY.json` y este informe; prompt `prompts/POST_V5/H1_AI_ONLY_INTEGRATED_DELIVERY.md` sin versionar. Tag `v5` intacto.

## 10. Recomendación
Aprobar H1 y autorizar commit/push. Antes de H2, decidir si se hará una validación **con provider real** de `interpret` (opcional, requiere autorización y configuración). Siguiente: `H2_HUMAN_DOCUMENTATION_BY_AUDIENCE` (no iniciado).
