# Pre-H5 Gate A — Portabilidad, independencia del runtime, validación estricta de entradas, IA opcional y contrato de rutas/recursos

**Estado: `PRE_H5_GATE_A_PORTABILITY = PASS`.** H5 = `NOT_STARTED`. Sin commit, push ni tag (autoridad Git: ninguna).

## 1. Alcance
Resuelve DT-01 (portabilidad / independencia del runtime), DT-02 (UX-01, rutas inválidas), DT-05 (proveedor de IA opcional) y DT-06 (contrato global de rutas/recursos).
No toca DT-03, DT-04, DT-07, DT-08, H5 ni V6.

Principio: *LegacyMapper depende de entradas explícitas y de recursos empaquetados, nunca de la máquina o carpeta donde se desarrolló.*

## 2. Cambios
| Archivo | Cambio |
|---|---|
| `legacy_documenter/utils/path_contract.py` (nuevo) | Contrato único: `validate_source_directory`, `validate_output_directory`, `validate_source_and_output`, `builtin_templates_root`, `PathContractError` (códigos estables). |
| `legacy_documenter/cli/full_pipeline.py` | `run_full_pipeline` valida fuente/salida antes de limpiar, escanear o escribir; devuelve `FAILED` con etapa `SCAN` / categoría `PATH_CONTRACT_VIOLATION`. |
| `legacy_documenter/main.py` | `analyze_repository` valida antes de escanear; `main` imprime el JSON del error en stderr y devuelve 4 (sin resumen "SUCCESS"/ni salida). |
| `legacy_documenter/behavior/template.py` | La raíz de plantillas integradas deja de ser `parents[2]/templates` (checkout) y pasa a `legacy_documenter/templates` (paquete). |
| `legacy_documenter/templates/{human,ai}` | Movidas desde `templates/` de la raíz del repositorio (sin cambios de contenido; los hashes de plantilla no cambian). |
| `legacy_documenter/behavior/prototype.py` | Valida `--source`/`--output` con el mismo contrato antes de cualquier trabajo. |
| `legacy_documenter/orchestration/ai_interpretation.py`, `legacy_documenter/llm/registry.py` | `_resolve_provider` llama a `ensure_provider_available` (sonda de disponibilidad en el borde de composición, sin importar el SDK desde `orchestration/`): si el SDK del proveedor seleccionado no está instalado falla de forma controlada (`PROVIDER_UNAVAILABLE`, `provider_called=false`). |
| `tests/test_post_v5_gate_a_portability.py` (nuevo) | 27 pruebas dirigidas. |
| `tests/test_post_v5_h4_template_productization.py`, `tests/test_v4_1_r0_maintainability_inventory.py` | Nueva ruta de plantilla; conteo de módulos 323 → 324 y nuevo snapshot de inventario. |
| `tests/test_v1_unittest.py`, `tests/test_v4_1_r7_exception_boundaries_characterization.py` | Cambio de disposición de fixtures (no de aserciones): la salida se escribía **dentro** del directorio fuente (`root/out`); ahora la fuente es `<tmp>/src` y la salida `<tmp>/out`, porque el contrato rechaza una salida dentro de la fuente de solo lectura. |
| `docs/POST_V5/PRE_H5_GATE_A_PORTABILITY_EVIDENCE.json` | Snapshot de inventario vivo (patrón de rondas anteriores) + módulos cambiados. |
| `README.md`, `PROJECT_STATE.json`, roadmap post-V5 | Estado y documentación. |

## 3. Contrato de rutas / recursos
**Entradas (fuente y salida)** — `path_contract.py`, evaluado antes de escáner, analizador, proveedor y cualquier escritura:

| Comprobación | Código | Exit |
|---|---|---|
| fuente inexistente / vacía | `SOURCE_PATH_NOT_FOUND` | 4 |
| fuente no es directorio | `SOURCE_PATH_NOT_DIRECTORY` | 4 |
| fuente ilegible | `SOURCE_PATH_NOT_READABLE` | 4 |
| salida existe y no es directorio / un padre es archivo | `OUTPUT_PATH_NOT_DIRECTORY` | 4 |
| salida o su ancestro existente no escribible (sonda real de creación/borrado; `os.access` no es fiable en Windows) | `OUTPUT_PATH_NOT_WRITABLE` | 4 |
| salida == fuente, dentro de la fuente, o fuente dentro de la salida (la fuente legacy es de solo lectura: AGENTS.md) | `SOURCE_OUTPUT_LAYOUT_CONTRADICTORY` | 4 |

**Cambio de comportamiento documentado:** antes `--output` dentro del repositorio fuente era aceptado (la salida contaminaba la fuente y la siguiente corrida la volvía a escanear); ahora es rechazado. Se reutiliza el contrato de códigos de salida existente (4 = FAILED); no se inventó uno nuevo. El error es legible (JSON con `message`) y detectable (`status: PATH_CONTRACT_VIOLATION`, `code`). Un padre de salida inexistente pero creable es válido (la validación no lo crea).
Normalización: `Path.resolve()` + `expanduser`; comparación de contención con `normcase`/`commonpath` (mayúsculas/minúsculas, unidades distintas). No se muta la intención del usuario.

**Recursos empaquetados** — precedencia: (1) argumento CLI explícito (`--template-dir`), (2) recurso integrado en el paquete (`legacy_documenter/templates`), (3) fallo claro. No se busca en directorios de desarrollo ni en el cwd. `runtime_resource_root()` es la única ancla permitida.

**Proveedor** — nada que resolver para `full`/`analyze`/`docs`/`visuals`/`deliver`. Para `interpret` la ubicación del ejecutable la resuelve el SDK del proveedor con su mecanismo documentado (`COPILOT_CLI_PATH`, PATH o runtime descargado); LegacyMapper no fija ni busca rutas. El workaround de proceso `COPILOT_CLI_PATH` de H4-R5 sigue siendo una variable de entorno opcional del usuario, no un requisito del producto.

## 4. UX-01
Antes: `full` sobre un repositorio inexistente → `SUCCESS` con análisis vacío (reproducido). Ahora: exit 4, JSON `SOURCE_PATH_NOT_FOUND` en stderr, **0 llamadas** a escáner/analizador/proveedor (verificado con dobles), la carpeta de salida **no se crea**. Mismo comportamiento en `analyze`.
Casos cubiertos por pruebas: fuente inexistente, fuente archivo, ilegible, salida archivo/bajo archivo, salida no escribible, layouts contradictorios, padres de salida creables, espacios, Unicode, relativas (fuente y salida), separador final, `.`, unidades distintas y diferencias de mayúsculas.

## 5. Clean-room
`tests.test_post_v5_gate_a_portability.CleanRoomTests` (y la validación IST de la sección 9):
* copia **solo** `legacy_documenter/` + `main.py` en `…\legacymapper-cleanroom-*\runtime dir\` (sin `tests/`, `docs/`, `tools/`, `templates/` de raíz);
* cwd = carpeta no relacionada; fuente `src ünï\repo` (espacios + Unicode) y salida `out put\o`, rutas absolutas;
* `full → docs → visuals → deliver` exit 0; plantilla integrada resuelta; PDFs, SVG y HTML generados; `interpret` → error controlado;
* `PYTHONDONTWRITEBYTECODE=1`, proveedor `NOT_INSTALLED`, sin `COPILOT_CLI_PATH` ni `PYTHONPATH`.
Limitación honesta: LegacyMapper no tiene `pyproject.toml`/`setup.py`; **no se probó instalación como paquete (pip/venv)**, solo la copia mínima de runtime. No se afirma portabilidad de instalación empaquetada.

## 6. Runtime de solo lectura
La copia de runtime y el repositorio fuente se marcan de solo lectura (atributo por archivo) y se toma un hash de árbol antes/después: **0 archivos nuevos/modificados** en runtime y fuente; ningún `__pycache__`. Los estados (caché `_cache_v53`, staging de `deliver` en el directorio temporal del sistema, salidas) van a la salida/temp permitidos.
Limitación: en Windows el atributo de solo lectura de un directorio no impide crear archivos, por lo que la garantía es la comparación de árbol (ningún intento de escritura tuvo efecto), no una denegación a nivel de ACL.

## 7. Proveedor ausente
| Caso | Resultado |
|---|---|
| `full`, `docs`, `visuals`, `deliver` con `ProviderRegistry.create`/`resolve_provider` parchados para fallar y SDK `copilot`/`openai` ausentes | exit 0, `provider_calls: 0`, nunca se tocó el proveedor |
| `interpret` con SDK `copilot` no instalado (por defecto COPILOT) | exit 1, `PROVIDER_UNAVAILABLE`, `provider_called: false`, 0 propuestas, línea base idéntica (solo aparece el directorio aislado `ai_runs/<id>` con su procedencia) |
| `interpret` con proveedor desconocido | exit 1, `PROVIDER_CONFIGURATION_ERROR` |
| ruta explícita del ejecutable (`COPILOT_CLI_PATH`) | llega intacta al SDK; el producto no la modifica |
No hay contenido inventado ni fallback silencioso.

## 8. Artefactos portables
* Paquete humano (fixture y IST): 0 coincidencias de rutas absolutas/`file:`/`AppData`/temporales/`PruebasLegacyMapper`/`IST_40` en HTML, SVG, JSON, CSS, MD y TXT; todos los enlaces `href/src` relativos y existentes; PDF sin URI `file:` ni rutas locales; el único `…:/` en SVG es el `xmlns` de W3C.
* Determinismo entre ubicaciones: la misma fuente en `A dir\` y `Ünï cödé B\` produce el mismo conjunto de archivos y **solo** difieren los archivos declarados de procedencia física/tiempo (`evidence/scan_summary.json`, `evidence/EVIDENCE_MANIFEST.json` —solo el hash de la partición `scan_summary`—, `index/repository.json`, `ai_context/SYSTEM_CONTEXT.json`, `_cache_v53/*`). IDs estables y todas las particiones de identidad son independientes de la ruta. Esta raíz física informativa es el contrato V5.9-R2 (`tests/test_v5_9_r2_source_identity.py`); **no se reescribió** (impacto: formato de Evidence y baseline IST persistido). Queda como deuda observada, no como defecto de ID/hash de identidad.

## 9. Validación IST (baseline persistido `IST_REAL_AI`, sin reanalizar)
Ejecutada desde una copia limpia del runtime, cwd ajeno, salidas fuera del baseline, proveedor `NOT_INSTALLED`:
| Comando | Resultado |
|---|---|
| `docs` | exit 0 · 24.6 s · `provider_calls 0` · `source_scanned false` |
| `visuals` | exit 0 · 18.4 s · 0 / false |
| `deliver` | exit 0 · 36.5 s · 0 / false · 1 584 archivos (igual que H4) |
| `interpret` | gate del baseline validado; exit 1 `PROVIDER_CONFIGURATION_ERROR`, `provider_called false` |
| Baseline | 47 529 archivos · 2 828 160 172 bytes · SHA-256 de árbol **idéntico antes y después** (`0b83011759221cec1b081611740607350eb34581817bfe01dfb7c693a7a67416`) |
| Paquete IST | 1 578 archivos de texto, 0 rutas absolutas/de desarrollo |
Escáner = 0, analizador = 0, proveedor = 0. (El hash completo del baseline de 2.8 GB tardó ~13 min por pasada; es el verificador, no el producto.)
La plantilla humana conductual (`behavior.prototype`) no se re-ejecutó contra IST (requiere fuente IST y es parte de H4-R5); su descubrimiento de plantilla se valida desde otro cwd y con `--template-dir` externo.

## 10. Auditoría de rutas codificadas
Búsqueda: `C:\`, `Users\`, `AppData`, `Temp\claude`, `scratchpad`, `PruebasLegacyMapper`, `dev\LegacyMapper`, `source\IST`, `cgalianj`, `COPILOT_CLI_PATH` sobre `legacy_documenter/`, `main.py`, `tools/`, `probe_*.py`.
| Ocurrencia | Clasificación |
|---|---|
| `evidence/persistence.py:9`, `exporters/markdown_exporter.py:14`, `exporters/_documentation_partitioning.py:106` (docstrings con ejemplos) | documentación/ejemplo |
| `knowledge/projection/{models,contract_report}.py` (`'C:'` como ejemplo de ruta rechazada) | contrato/ejemplo |
| falsos positivos de la expresión (`RENDER_HUMAN_DOC`, `SYMMETRIC:`) | no son rutas |
| `tools/v5_1_r2_real_ist_regression.py`, `tools/v5_3_r2_9_calibrate.py` | herramienta de desarrollo (no viaja en el runtime) |
| **defectos de runtime** | **ninguno**; `behavior/template.py` dependía del checkout (`parents[2]`) → corregido |
Una prueba (AST, literales de cadena no-docstring del paquete) impide reintroducirlas, y otra prohíbe `getcwd`/`Path.cwd`/`parents[2]` en el runtime.

## 11. Pruebas
* Dirigidas: `tests.test_post_v5_gate_a_portability` — **27 pruebas, OK** (~39 s).
* Relacionadas: plantillas H4, H1 AI-only, guarda de proveedor real, H4-R4, inventario de mantenibilidad, huellas/versionado — OK.
* Suite completa (una vez, al final): ver sección 12.

## 12. Suite completa
`python -X utf8 -m unittest discover -s tests`
| Medida | Resultado |
|---|---|
| Total | **3 361** (3 334 previos + 27 nuevos) |
| Fallos / errores | **0 / 0** |
| Skips | 132 (los históricos; ninguno nuevo) |
| Duración | 1 118 s (1 125 s de pared) |
| Exit code | **0** |

Historia honesta de la ejecución: la primera corrida completa detectó 32 problemas reales causados por este gate (31 tests históricos escribían la salida dentro de la fuente → fixtures reubicados; 1 guarda de arquitectura por un `importlib`), la segunda 1 más (una guarda de límites neutrales: la sonda del SDK estaba en `orchestration/`; movida a `llm/registry.py`). La tercera corrida, sobre el árbol final, es la que se reporta arriba. Las dos primeras no se cuentan como validación del árbol final.

## 13. Deuda restante
Sin declarar resueltas: **Gate B** — DT-03 UI/navegación/estilos → Evidence Core. **Gate C** — DT-04 resolución BL entre proyectos, DT-07 segunda plantilla humana, DT-08 deuda menor seleccionada. UX-03 (CLI de consumers) sin tocar. Observaciones nuevas:
1. `behavior/prototype.py` conserva valores por defecto específicos de IST (`--project WebPREPrevencion`, `--solution slnPREPrevencion_2010`): no son rutas, pero acoplan el prototipo al proyecto de desarrollo (candidato a DT-08).
2. `scan_summary.root` / `source_repository` persisten la ruta física (informativa, contrato V5.9-R2); evaluar una proyección lógica en un cambio de formato de Evidence (Gate B).
3. Instalación empaquetada (pip/venv) no probada: no hay metadatos de empaquetado en el repositorio.
4. `output-manifest` con un directorio inexistente aún propaga `FileNotFoundError` (contrato histórico V4.3-R7), fuera del alcance de este gate.
