# Post-V5 — Preparación del checkpoint final de Git

Documento de ronda (histórico). Estado vigente: `PROJECT_STATE.json`. **Nada fue staged, commiteado, subido ni etiquetado.**

## Estado

```text
H1-H5 = CLOSED    POST_V5 = CLOSED    V6 = NOT_STARTED
POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE = PASS
EXTERNAL_HISTORICAL_FIXTURE_DEPENDENCIES = 0   ACTIVE_ABSOLUTE_WORKSPACE_DEPENDENCIES = 0
BLOCKING_HYGIENE_DEBT = 0   OLD_CLONE_UNIQUE_CURRENT_CODE = 0   ROOT_AD_HOC_PROBES = 0
provider calls = 0   análisis IST = 0
```

## Resumen del árbol de trabajo (rama `main`, upstream `origin/main`, base `9b4f165`)

| Categoría | Rutas | Clasificación |
| --- | --- | --- |
| Código de producto (correcciones H5) | `legacy_documenter/behavior/{evidence,explain,prototype,wireframe}.py`, `legacy_documenter/product/package.py` | KEEP_AND_COMMIT |
| Higiene de código | `legacy_documenter/devtest.py` (nuevo), `legacy_documenter/evidence/persistence.py` (docstring) | KEEP_AND_COMMIT |
| Tests | `tests/test_post_v5_h5_real_ist_scale.py`, `tests/test_post_h5_hygiene.py` (nuevos); `test_v4_1_r0_maintainability_inventory.py` (pin 335), `test_v4_3_r3a_r1_…` (REAL_IST por variable de entorno) | KEEP_AND_COMMIT |
| Tools | `tools/v5_1_r2_real_ist_regression.py`, `tools/v5_3_r2_9_calibrate.py` (env vars); `tools/provider_probes/` (nuevo: 3 sondas + README) | KEEP_AND_COMMIT |
| Sondas de la raíz | `probe_copilot.py`, `probe_legacymapper_provider.py` (movidas); `probe_copilot_request.py`, `probe_real_flow.py`, `probe_real_flow_raw.py` (eliminadas) | KEEP_AND_COMMIT (renombrado/borrado) |
| Prompts | 203 archivos movidos a `prompts/archive/{V4,V4_1,V4_2,V4_3,V5_0,V5,POST_V5}`; `prompts/CURRENT/README.md` nuevo; 3 prompts nuevos de H5/higiene en `archive/POST_V5` | ARCHIVE → KEEP_AND_COMMIT |
| Docs vigentes | `docs/OPERATIONS/{RESUME_LEGACYMAPPER,WORKSPACE_CONTRACT,TESTING_GUIDE}.md`, `docs/ARCHITECTURE/CURRENT_ARCHITECTURE.md` | KEEP_AND_COMMIT |
| Docs de ronda | `docs/POST_V5/H5_REAL_IST_VALIDATION_{AND_CLOSURE_RESULT.md,EVIDENCE.json}`, `POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE_RESULT.md`, este informe | KEEP_AND_COMMIT |
| Estado/gobernanza | `PROJECT_STATE.json`, `README.md`, `CLAUDE.md`, roadmap Post-V5 (banner + §19), manuales V4 (`prompts/archive/V4/`), `PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json` (solo bloque `inventory`) | KEEP_AND_COMMIT |

Excluidos intencionalmente (`GENERATED_DO_NOT_COMMIT`, ya ignorados por `.gitignore`): `__pycache__/`, `build/`,
`legacymapper.egg-info/`, `output/_local_*/`, `docs/V4_3/samples/R6/parts/`. No hay rutas `UNRELATED` ni
`DELETE_BEFORE_COMMIT` pendientes. Aviso: Git avisa de conversión LF→CRLF en 4 archivos editados; es inocuo.

## Workspace externo

Antes 73,92 GiB → después 3,48 GiB (recuperados ≈ 70,44 GiB). Retenido: `Current/state/{baseline,ai}`,
`Current/reference/final_human_sample`, `Archive/` (respuestas de IA históricas únicas, targets del piloto Python).
`Archive/LegacyMapper_old_clone` aún existe: sin código único (lo útil se migró), su borrado requiere tu autorización
explícita (el clasificador bloqueó el `rm -rf`). Detalle: `STORAGE_CLEANUP_POST_H5_RESULT.md` en el workspace.

## Resultado de tests

* Suite completa (tras la higiene del repositorio, antes de la finalización): **3575 tests, 0 fallos, 0 errores, 135 skips** (explícitos).
* Tras la finalización (sondas, documentos de estado), solo perfiles dirigidos: `fast` 152 OK · `provider` 75 OK ·
  `distribution` 173 OK · módulos que leen `PROJECT_STATE.json` + `test_post_h5_hygiene` 637 OK.
* No se repitió la suite completa tras la finalización: los cambios fueron sondas fuera del runtime y documentación/estado.
  Recomendado correrla una vez antes del commit si se quiere el recibo completo.

## Recomendación

* Rama: `main`, upstream `origin/main` (sin ramas nuevas).
* Mensaje de commit: `Finalize Post-V5 and repository hygiene`
* Orden: (1) opcional, suite completa; (2) revisar `git status`; (3) `git add -A` (los renombrados de prompts se
  detectan como `R`); (4) commit; (5) push; (6) etiqueta solo si el responsable la decide. V6 sigue `NOT_STARTED`.
