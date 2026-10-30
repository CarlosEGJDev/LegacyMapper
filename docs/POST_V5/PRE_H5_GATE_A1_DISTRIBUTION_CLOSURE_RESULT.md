# Pre-H5 Gate A.1 — Distribución, defaults genéricos y cierre de fallas controladas del CLI

**Estado: `PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS`.** `PRE_H5_GATE_A_PORTABILITY = PASS` se mantiene. H5 = `NOT_STARTED`. Sin commit, push ni tag.

## 1. Alcance
A1-01 distribución/instalabilidad real · A1-02 defaults genéricos del prototipo conductual · A1-03 `output-manifest` con falla controlada.
Fuera de alcance (no tocado): UI/navegación → Evidence Core, BL entre proyectos, rediseño de la procedencia física `scan_summary.root` (se registra para Gate B), segunda plantilla, CLI de consumers.

## 2. Cambios
| Archivo | Cambio |
|---|---|
| `pyproject.toml` (nuevo, raíz) | Empaquetado estándar (setuptools): paquete `legacymapper` 5.9.0, sin dependencias requeridas, extra opcional `copilot`, script `legacymapper`, `package-data` json/html/css/yaml/md. Solo incluye `legacy_documenter*`. |
| `legacy_documenter/__main__.py` (nuevo) | `python -m legacy_documenter` (mismo punto de entrada que `main.py` y el script de consola). |
| `legacy_documenter/behavior/prototype.py` | Sin defaults de IST: `--project`/`--solution` son opcionales solo si hay un único candidato; `SelectionError` con códigos estables. Se registra `baseline.project_solution_selection`. |
| `legacy_documenter/behavior/evidence.py` | `solution_has_project` extraído a función de módulo (compartido por el explicador y la regla de selección; sin cambio de lógica). |
| `legacy_documenter/utils/path_contract.py` | `validate_existing_output_directory` y códigos `OUTPUT_MANIFEST_INPUT_NOT_FOUND` / `_NOT_DIRECTORY` (mismo contrato y forma de error que Gate A). |
| `legacy_documenter/cli/router.py` | `output-manifest` valida con el contrato antes de construir/escribir. |
| `tests/test_post_v5_gate_a1_distribution.py` (nuevo) | 22 pruebas. |
| `tests/test_v4_3_r7_internal_acceptance.py` | Un test histórico actualizado al nuevo contrato de `output-manifest` (ver sección 7). |
| `tests/test_v4_1_r0_maintainability_inventory.py`, `docs/POST_V5/PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE_EVIDENCE.json` | Conteo 324 → 325 módulos y nuevo snapshot de inventario. |

## 3. A1-01 — Distribución instalada
Artefacto: **wheel** `legacymapper-5.9.0-py3-none-any.whl` (~0.8 MB, 378 entradas), construido por `pip wheel` desde una **copia** de `pyproject.toml` + `legacy_documenter/` (el checkout no se contamina con `build/` ni `egg-info`).
Contenido verificado: `templates/human/default/{template.yaml,document.html,styles.css,pdf.css}`, `templates/ai/README.md`, los 42 recursos `documentation_v52/defaults/**` y el `entry_points.txt`; sin `tests/`, `tools/`, `docs/`, `output/`, `prompts/`, `codex/` ni `__pycache__`.

Prueba reproducible (clase de rutas: `<tmp>/…`; cwd deliberadamente fuera del checkout y con Unicode):
```text
python -m pip wheel --no-deps -w <tmp>/dist <tmp>/src          # src = pyproject.toml + legacy_documenter/
python -m venv <tmp>/venv
<tmp>/venv/Scripts/python -m pip install --no-deps --no-index <tmp>/dist/legacymapper-5.9.0-py3-none-any.whl
cd "<tmp>/cwd ñ"           # sin PYTHONPATH, sin COPILOT_CLI_PATH, sin SDK de proveedor (pip list: solo legacymapper y pip)
legacymapper full <fixture> --output "<tmp>/out ü"             -> SUCCESS
legacymapper docs|visuals|deliver "<tmp>/out ü"                -> SUCCESS, provider_calls 0
legacymapper interpret "<tmp>/out ü"                           -> exit 1, PROVIDER_UNAVAILABLE, provider_called false
legacymapper output-manifest <tmp>/nope                        -> exit 4, OUTPUT_MANIFEST_INPUT_NOT_FOUND, sin traceback
python -c "import legacy_documenter; print(legacy_documenter.__file__)"  -> <tmp>/venv/Lib/site-packages/legacy_documenter/__init__.py
```
Las mismas verificaciones están automatizadas (`InstalledDistributionTests`): `--help` por ambos puntos de entrada, `full` con fuente con espacios/Unicode y salida en otra carpeta, `docs`/`visuals`/`deliver`, descubrimiento de la plantilla integrada, `--template-dir` externo (sin mutar la integrada), `interpret` sin proveedor, entradas inválidas sin traceback, y que `__file__`/`builtin_templates_root()` estén en `site-packages` y nunca bajo el checkout. Si la máquina no puede obtener un backend PEP 517 (sin red ni `setuptools`), esas pruebas se **omiten con motivo explícito**, no pasan en silencio.
Un test adicional falla si aparece un tipo de recurso no declarado como package-data. `python main.py …` y `python -m legacy_documenter` se verifican desde el checkout (compatibilidad).
Límites honestos: validado solo con Python 3.14.7 (`requires-python >= 3.12` es un piso no probado por debajo); se probó wheel (no sdist ni PyPI); el venv se probó en Windows.
Nota de proceso: construir el wheel descarga `setuptools` (aislamiento de build) hacia un entorno temporal; no se instaló nada en el Python del sistema.

## 4. A1-02 — Selección genérica de proyecto/solución
Regla (solo con evidencia persistida; nada se inventa): candidatos de proyecto = proyectos del baseline con al menos un ítem `.ascx/.aspx`.
| Situación | Resultado |
|---|---|
| `--project` explícito inexistente | `PROJECT_NOT_FOUND` (+ candidatos) |
| 0 candidatos | `NO_BEHAVIORAL_PROJECT_CANDIDATES` |
| 1 candidato | seleccionado de forma determinista y registrado (`deterministic_single_candidate`) |
| >1 | `PROJECT_SELECTION_REQUIRED` (lista ordenada) |
| solución: 0 / 1 / >1 / inexistente | `NO_SOLUTION_CANDIDATES` / determinista / `SOLUTION_SELECTION_REQUIRED` / `SOLUTION_NOT_FOUND_FOR_PROJECT` |
Exit 4, JSON en stdout (convención del prototipo), sin escribir salida. Los literales `WebPREPrevencion`, `slnPREPrevencion_2010`, `IST_40`, `PREPrevencion` ya no existen en ningún archivo del paquete (prueba de auditoría de literales + prueba AST de defaults `None`).

## 5. A1-03 — `output-manifest`
Antes: `FileNotFoundError` con traceback. Ahora: directorio inexistente → `OUTPUT_MANIFEST_INPUT_NOT_FOUND`, ruta que es archivo → `OUTPUT_MANIFEST_INPUT_NOT_DIRECTORY`, no escribible → `OUTPUT_PATH_NOT_WRITABLE`; todos con exit 4 y JSON `PATH_CONTRACT_VIOLATION` en stderr, sin escribir nada. La API de biblioteca `build_output_manifest` conserva su contrato histórico. `docs`, `visuals`, `deliver` e `interpret` ya fallaban por contrato ante un baseline inexistente (exit 4, `*_INVALID`); queda cubierto por prueba.

## 6. Procedencia física de la fuente
`scan_summary.root` / `source_repository` **no se rediseñaron**: pasan a Gate B (puede afectar el formato/proyección de Evidence).

## 7. Pruebas
* Dirigidas: `tests.test_post_v5_gate_a1_distribution` — **22 pruebas, OK** (~80 s, incluye build + venv + instalación).
* Relacionadas (Gate A, H4, inventario, guardas de arquitectura, huellas): OK.
* Suite completa (una vez, sobre el árbol final): `python -X utf8 -m unittest discover -s tests`

| Medida | Resultado |
|---|---|
| Total | **3 383** (3 361 previos + 22 nuevos) |
| Fallos / errores | **0 / 0** |
| Skips | 132 (históricos; ninguno nuevo) |
| Duración | 837.8 s |
| Exit code | **0** |

Historia honesta: la primera corrida completa dio 1 error — `tests/test_v4_3_r7_internal_acceptance.py` fijaba que la ruta `output-manifest` propagara `FileNotFoundError`, que es exactamente el comportamiento que A1-03 reemplaza. La prueba se actualizó al nuevo contrato (`PathContractError` / `OUTPUT_MANIFEST_INPUT_NOT_FOUND` en la ruta; la API de biblioteca sigue lanzando `FileNotFoundError`) y la suite completa se **repitió** sobre el árbol final; solo esta segunda corrida se reporta como validación.

## 8. Deuda restante (no declarada resuelta)
**Gate B:** DT-03 UI/navegación/estilos → Evidence Core + evaluar proyección física vs lógica de la procedencia de la fuente.
**Gate C:** DT-04 BL entre proyectos, DT-07 segunda plantilla humana, DT-08 deuda menor restante, decisión UX-03.
Observaciones: sdist/publicación en un índice no evaluados; instalación probada solo en Windows/Python 3.14.
