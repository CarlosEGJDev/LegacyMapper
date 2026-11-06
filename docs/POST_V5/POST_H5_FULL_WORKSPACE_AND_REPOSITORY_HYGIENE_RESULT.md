# Post-H5 — Higiene completa de workspace y repositorio: resultado

Documento histórico/específico de esta ronda. El estado vigente está en `PROJECT_STATE.json`.

## Veredicto

```text
POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE = PASS

EXTERNAL_HISTORICAL_FIXTURE_DEPENDENCIES = 0
ACTIVE_ABSOLUTE_WORKSPACE_DEPENDENCIES   = 0
BLOCKING_HYGIENE_DEBT                    = 0
OLD_CLONE_UNIQUE_CURRENT_CODE            = 0
ROOT_AD_HOC_PROBES                       = 0

H5 = CLOSED   POST_V5 = CLOSED   V6 = NOT_STARTED
provider calls = 0   análisis IST = 0   commit/push/tag = NO
```

## Almacenamiento (`<WORK_ROOT>` = `C:\PruebasLegacyMapper`)

| Métrica | Valor |
| --- | --- |
| Antes | 79 368 648 709 B (73,92 GiB), 651 542 archivos |
| Después | 3 737 587 547 B (3,48 GiB), 50 196 archivos |
| Recuperado | 75 631 061 162 B (≈ 70,44 GiB) |
| Baseline retenido | 3 704 639 067 B (una copia; antes 6+ copias idénticas) |
| IA retenida | 4 433 294 B (`Current/state/ai`, 240 archivos) + Archive |
| Detalle | `STORAGE_INVENTORY_POST_H5.md/.json` y `STORAGE_CLEANUP_POST_H5_RESULT.md` en el workspace |

El borrado fue autorizado explícitamente por el responsable tras un primer bloqueo del clasificador de permisos;
se ejecutó con el alcance exacto (carpetas `_OFF_*` y `ProyectoRealPrueba`). La suite completa se ejecutó con esas
carpetas fuera de su ubicación original, por lo que ya probaba la independencia.

Copias del baseline de 3,5 GB: 6+ idénticas → 1 (`Current/state/baseline`, árbol SHA-256 `e39bf2ac…ce20`; H4 verificado
idéntico salvo `index/repository.json`, dato de máquina). Respuestas de IA: únicas por SHA-256 (H5: 242 → 240 archivos,
2 `TEMPLATE_MANIFEST.json` duplicados; 69 de H4 sin duplicados contra H5; 10 únicas de otras rondas).

Retenido: `Current/state/{baseline,ai}`, `Current/reference/final_human_sample` (paquete H4 aprobado),
`Archive/ai_responses_historical/{h4,other_runs}`, `Archive/V5_acceptance_targets`,
`Archive/LegacyMapper_old_clone` (clon V4.2, sin commits sin subir; 3 scripts sin versionar; **revisión manual**).
La fuente IST real (`<SOURCE_ROOT>`) no fue tocada.

## Dependencias de fixtures externos eliminadas

* Único test activo con dependencia externa: `test_v4_3_r3a_r1…` T9 leía `Resultados\v4_3_rebaseline`; ahora es
  `REAL_IST_EXTERNAL` configurado por `LEGACYMAPPER_REAL_IST_BASELINE` (skip con razón explícita).
* `tools/v5_1_r2_real_ist_regression.py`, `tools/v5_3_r2_9_calibrate.py`: rutas de máquina → variables de entorno.
* `legacy_documenter/evidence/persistence.py`: docstring sin ruta de máquina.
* Tests con `skipUnless(output/v2_r5_1_full…)` son opcionales (skip si faltan); `output/v3_r8_1` está versionado en el repositorio.
  `HISTORICAL_SNAPSHOT` requerido por tests activos = **0**.
* Test de contrato permanente: `tests/test_post_h5_hygiene.py` (sin rutas de máquina en tests/runtime/tools/docs operativos).

Auditoría de rutas absolutas en `legacy_documenter/`, `tests/`, `tools/`, `pyproject.toml`, `README.md`, `docs/OPERATIONS`:
`ACTIVE_DEPENDENCY = 0`. Restan, como `HISTORICAL_RECORD`/`DOC_EXAMPLE`: `AGENTS.md` y `docs/PROJECT_RECOVERY.md`
(ruta de la fuente en la máquina del operador, gobernanza del propietario, no se tocó), `PROJECT_STATE.json`
(rutas históricas, con nota), reportes en `docs/V*` y `docs/POST_V5`, y datos de ejemplo/negativos en 5 tests.

## Perfiles de test (`python -X utf8 -m legacy_documenter.devtest <perfil>`)

FAST (<1 min), CORE, ANALYSIS, BEHAVIOR (~10 s), HUMAN_DOCS, AI_KNOWLEDGE, VISUALS, PACKAGING (~1,5 min),
DISTRIBUTION, PROVIDER, REAL_IST, FULL; más `list`, `suggest <ruta>` y `changed` (mapa ruta → perfil).
Cada perfil documenta propósito, dependencias externas, uso y duración (`legacy_documenter/devtest.py`,
`docs/OPERATIONS/TESTING_GUIDE.md`). Un test verifica que ningún módulo de `tests/` quede sin perfil.
Verificados en vivo: FAST, BEHAVIOR (45 tests), PACKAGING (202) y DISTRIBUTION (173) — este último detectó una
referencia `prompts/V4/` rota en dos manuales históricos V4, ya corregida.

## Tests históricos

121 módulos (v1: 2, v3: 24, v4: 14, v4.1: 10, v4.2: 10, v4.3: 12, v5: 27, post-v5: 21, hygiene: 1). **Ninguno
eliminado**: no se probó cobertura equivalente. Clasificación: `AUTHORITATIVE_REGRESSION` (v4_r*, v4.1–v4.3, v5.*,
post-v5 — protegen contratos vigentes), `HISTORICAL_ONLY` (v1, v3: se mantienen por auditoría), `OBSOLETE` = 0,
`DUPLICATED_COVERAGE` = no determinado (candidato a un análisis futuro). Se agregó `test_post_h5_hygiene` (13 tests)
y se actualizó el pin de 334→335 archivos de producción (+`devtest.py`) con su snapshot regenerado
(`PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json`, solo el bloque `inventory`).

Regresiones H5 intactas en `tests/test_post_v5_h5_real_ist_scale.py` (membresía exacta, paquete solo-máquina,
ids de datos, wireframes dentro del marco, sin propósito inferido del nombre).

## Prompts

203 prompts movidos con `git mv` a `prompts/archive/{V4,V4_1,V4_2,V4_3,V5_0,V5,POST_V5}`; `prompts/CURRENT/README.md`
declara `POST_V5 CLOSED / H1-H5 CLOSED / V6 NOT_STARTED / sin prompt activo`. `CLAUDE.md` (lista de lectura) apunta
al nuevo punto de entrada. Referencias a las rutas viejas en docstrings/reportes históricos se conservan.

## Documentación canónica creada

`docs/OPERATIONS/RESUME_LEGACYMAPPER.md`, `docs/OPERATIONS/WORKSPACE_CONTRACT.md`, `docs/OPERATIONS/TESTING_GUIDE.md`,
`docs/ARCHITECTURE/CURRENT_ARCHITECTURE.md`; `README.md` (sección «Dónde leer» con lo vigente y lo histórico);
`PROJECT_STATE.json` (bloque `post_h5_hygiene`; corregido `"h5": "NOT_STARTED"` obsoleto → `CLOSED`).

## Prueba de relocalización

Con datos sintéticos pequeños, sin análisis IST: `tests/test_post_h5_hygiene.py::WorkspaceRelocationTests` genera
un baseline, lo **mueve** a una ruta con espacios y Unicode y ejecuta `docs`, `visuals` y `deliver` desde un cwd
ajeno (0 llamadas a proveedor, 0 reescaneos). Además `test_post_v5_gate_a_portability` ya prueba repositorio/runtime
en otra ruta, salida con espacios y Unicode, cwd ajeno y wheel aislada.

## Suite final

```text
python -X utf8 -m unittest discover -s tests   (sin LEGACYMAPPER_REAL_IST_BASELINE; carpetas históricas externas renombradas)
Ran 3575 tests in 805,8 s — OK (skipped=135): 0 fallos, 0 errores
```

Los 3 skips nuevos respecto de H5 (132 → 135) son integraciones externas ahora omitidas con razón explícita.
Una ejecución previa detectó 2 fallos propios (pin de 334 archivos y snapshot de inventario por el nuevo `devtest.py`);
corregidos y la suite se repitió completa.

## Finalización (POST_H5_HYGIENE_FINALIZATION_AND_GIT_READINESS)

**Decisión A — `Archive/LegacyMapper_old_clone`**: sin commits sin publicar (`origin/main..HEAD` = 0), sin stash;
solo 3 scripts sin versionar.

| Archivo | Clasificación | Motivo |
| --- | --- | --- |
| `list_copilot_models.py` | MIGRATE_TO_CURRENT_REPO → `tools/provider_probes/` | Diagnóstico genérico y vigente (lista modelos del SDK), sin rutas de máquina |
| `test_flow_ai.py` | DELETE | Ruta fija al workspace ya borrado; capacidad cubierta por `main.py interpret` |
| `test_flow_ai_hydrated.py` | DELETE | Ídem |

Todo lo útil quedó en el repositorio (`OLD_CLONE_UNIQUE_CURRENT_CODE = 0`). El directorio del clon sigue en
`Archive/` a la espera de autorización explícita para borrarlo (no estaba cubierta por el borrado anterior).

**Decisión B — sondas de la raíz**

| Sonda | Clasificación | Resultado |
| --- | --- | --- |
| `probe_copilot.py` | CURRENT_DIAGNOSTIC_TOOL | → `tools/provider_probes/probe_copilot_sdk.py` |
| `probe_legacymapper_provider.py` | CURRENT_DIAGNOSTIC_TOOL | → `tools/provider_probes/` (con `sys.path` a la raíz del repo) |
| `probe_copilot_request.py` | DUPLICATED_CAPABILITY | eliminado (duplica la sonda del proveedor de LegacyMapper) |
| `probe_real_flow.py`, `probe_real_flow_raw.py` | HISTORICAL_EXPERIMENT | eliminados (rutas de máquina y flujo fijo; camino soportado: `interpret`) |

`tools/provider_probes/README.md` documenta propósito, uso, variables de entorno y advertencia de proveedor real/cuota.
La raíz del repositorio solo contiene `main.py` como script (`ROOT_AD_HOC_PROBES = 0`).

**Estado documental**: corregidos textos obsoletos (`README.md`, roadmap Post-V5 con banner y §19, `PROJECT_STATE.json`
`next`). `H5 = CLOSED`, `POST_V5 = CLOSED`, `V6 = NOT_STARTED` en todos los documentos de autoridad.

**Tests dirigidos tras los cambios**: ver `docs/POST_V5/POST_V5_FINAL_GIT_READINESS.md`.

## Deuda de higiene restante (no bloqueante)

1. Borrado de `Archive/LegacyMapper_old_clone` (sin código único; pendiente de autorización explícita).
2. `AGENTS.md` / `docs/PROJECT_RECOVERY.md` mantienen la ruta de la fuente del operador.
3. `DUPLICATED_COVERAGE` en tests históricos sin evaluar.
4. Git: sin commit/push/tag; checkpoint pendiente de autorización.
