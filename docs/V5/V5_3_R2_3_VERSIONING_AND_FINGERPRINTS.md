# V5.3 R2.3 — Versionado y fingerprints

Estado final: **V5_3_R2_3_READY_FOR_REVIEW**

## 1. Objetivo

Exponer en el runtime, sin consumirlos todavía, los valores que necesitará la futura caché de extracción (R1 §4–5): `ANALYZER_VERSION`, `ANALYZER_CODE_FINGERPRINT`, `CONFIG_FINGERPRINT`, `TEMPLATE_PROFILE_FINGERPRINT`, registro de versiones de renderers y hash semántico; más tests guardianes. Sin File State, sin `_cache_v53/`, sin cambios de flujo.

## 2. Corrección documental realizada

En `docs/V5/V5_3_R2_2_1_MAINTAINABILITY_AND_FINAL_VALIDATION.md` §17, la frase que indicaba el cierre Git de V5.2 como `PENDING_GIT_APPROVAL` ahora dice que ya está hecho (commit, tag `v5.2`, publicación en `origin/main`). Solo esa frase. (Verificado localmente: tag `v5.2` existe y `origin/main` está presente; la publicación remota la afirma el prompt, no la comprobé contra el remoto.)

## 3. Archivos modificados

| Archivo | Cambio |
|---|---|
| `legacy_documenter/versions.py` (**nuevo**, 51 líneas) | `ANALYZER_VERSION`, `LEGACY_MARKDOWN_RENDERER_VERSION`, `evidence_schema_version()`, `renderer_versions()` |
| `legacy_documenter/fingerprints/` (**nuevo**, paquete de 6 módulos) | `_common`, `code`, `configuration`, `templates`, `semantic`, `__init__` (API pública) |
| `tests/test_v5_3_r2_3_versioning_and_fingerprints.py` (**nuevo**, 55 tests) | ver §13 |
| `tests/test_v4_1_r0_maintainability_inventory.py` | inventario congelado: +7 módulos, categorías, módulos con acceso a archivos, `module_count` +60 |
| `docs/V5/V5_3_R2_2_1_…md` | una frase (§2) |

No se tocó ningún módulo de producción existente, `PROJECT_STATE.json`, Evidence Core, IDs ni manifests. Nada del runtime importa los módulos nuevos (lo verifica un test).

## 4. `ANALYZER_VERSION`

Entero, `1`, en `versions.py`. Cubre extracción, scanner/clasificación, namespaces/partial, resolvers, sanitizer. No usa Git. Guardián en §14.

## 5. `ANALYZER_CODE_FINGERPRINT`

`analyzer_code_fingerprint(package_root=None) -> CodeFingerprint(status, sha256, file_count, reason)`. SHA-256 de registros `(etiqueta, contenido)` con prefijo de longitud, ordenados por etiqueta (rutas relativas POSIX), más un tag de algoritmo.

Incluye: `extractors/`, `analysis/`, `scanner/`, `models/` (todos los `*.py`), `utils/sanitizer.py`, `config.py` y **solo** estas funciones de `cli/pipeline_stages.py` (por AST): `scan_repository`, `extract_repository`, `_extract_into`, `apply_project_namespaces`, `consolidate_partial_symbols`, `_norm_path`, `resolve_calls`, `resolve_web_entries`, `resolve_database`, `resolve_flows`, `resolve_dependencies`. Un cambio en el resto de ese módulo (render/escritura) no invalida.

Saltos de línea de las fuentes normalizados a LF (un checkout CRLF no cambia el valor). Sin timestamps, Git, docs, prompts, tests ni `PROJECT_STATE.json`. Fuentes ausentes/ilegibles, directorio sin `.py` (solo `.pyc`), función ausente o `pipeline_stages.py` no parseable → `status="unavailable"`, `sha256=None`, con `reason` (la futura caché debe tratarlo como "no reutilizar extracción"). Valor actual: `81168845…759e`, 49 fuentes.

## 6. `EVIDENCE_SCHEMA_VERSION`

Reutilizada (`evidence.entities.EVIDENCE_SCHEMA_VERSION = "1.0"`) vía `versions.evidence_schema_version()`; test: misma identidad de objeto y ninguna redefinición.

## 7. `RENDERER_VERSIONS`

`renderer_versions()` devuelve un mapa por familia (importes diferidos, constantes reutilizadas):

| Familia | Fuente |
|---|---|
| `legacy_markdown` | **nueva** `LEGACY_MARKDOWN_RENDERER_VERSION = "1"` (no existía) |
| `human_documentation` | `MODEL_VERSION`/`SCHEMA_VERSION` de `human_flow_documentation` (V4.3-R3, 1.0) y `human_documentation_scaling` (V4.3-R4, 1.0) |
| `consumer_projection` | `CONTRACT_VERSION`/`SCHEMA_VERSION` (1.0) |
| `ai_context` | `SystemContextBuilder.MODEL_VERSION` (V2-R5) + `ai_projection` 1.0 |
| `hydration` | `hydration.MODEL_VERSION` (V4.3-R3) |
| `documentation_v52` | `config.CONTRACT_VERSION` ("1") |

Un test congela el mapa actual (esta ronda no cambia contratos de salida). Metadata Git: no se registró (opcional; no debe ser clave).

## 8. `CONFIG_FINGERPRINT`

Separado en dos partes (justificación: la caché de extracción solo debe invalidarse por lo que cambia extracción; las proyecciones se regeneran siempre, R1 DEC-00) y combinado:

- `analysis_config_fingerprint(excludes, flow_max_depth)`: `DEFAULT_EXCLUDES`, `VTI_PREFIX`, `TEXT_EXTENSIONS` (leídos de `config` en cada llamada), `--exclude` como conjunto (orden y duplicados irrelevantes; **sensible a mayúsculas**, como el scanner), `flow_max_depth`.
- `projection_config_fingerprint(profiles, custom_dir, strict_templates)`: perfiles activos (el orden importa), `strict_templates` y el fingerprint de templates/perfiles (que incluye idiomas y `custom_dir`).
- `config_fingerprint(...)`: ambos combinados (el `CONFIG_FINGERPRINT` de R1).

Fuera de todos: `allow_ai_interpretation`, `--verbose`, `--long-paths`, rutas de salida, `repository`.

## 9. Clasificación de opciones CLI

Fuente: `fingerprints.CLI_OPTION_CLASSES`, contrastada por test contra `build_parser()` real (enumera todos los subparsers; falla ante opción sin clasificar o entrada obsoleta).

| Opción (dest) | Clase |
|---|---|
| `exclude`, `flow_max_depth` | analysis-affecting |
| `verbose`, `long_paths` | runtime-only |
| `allow_ai_interpretation` | ai-only |
| `output`, `output_dir` | output-location-only |
| `repository` | **repository-identity** (sexta clase, ver nota) |

Nota: el prompt lista cinco clases; añadí `repository-identity` porque la entrada no encaja en ninguna: su contenido lo cubren los hashes por archivo y la futura `repository_identity` (R1 §6), y su ruta no debe entrar al fingerprint de configuración. Es una decisión revisable. No hay opciones projection-affecting en el CLI actual; los parámetros de biblioteca de `generate_documentation_v52` se clasifican en `V52_PARAMETER_CLASSES` (test: coincide con la firma real). `long_paths` se clasificó runtime-only (cambia la forma de escribir, no el contenido).

## 10. `TEMPLATE_PROFILE_FINGERPRINT`

`template_profile_fingerprint(profiles, custom_dir, defaults_dir)`: SHA-256 del contenido (LF-normalizado) de `defaults/{templates,profiles,i18n,noise}/**/*.json` y equivalentes de `custom_dir` (etiquetados `custom/…`), más perfiles activos, idioma efectivo de cada uno (custom sobre default) y presencia de `custom_dir`. Independiente de orden de lectura, mtime y rutas absolutas. Un archivo ilegible lanza `OSError`. No se modificó ningún default. Valor actual: `7b5419b0…`.

## 11. Hash semántico

`semantic_content_sha256(bytes, file_type) -> str | None`, `semantic_file_sha256(path, file_type)`. Solo `ANALYZED_FILE_TYPES` (`solution`, `vb_project`, `vb_source`, `aspx`, `ascx`, `master`, `web_config`; un test exige que coincida con el mapa de extractores de `extract_repository`); cualquier otro tipo → `None` (se usa el hash crudo). Normaliza CRLF y CR suelto a LF sobre bytes; BOM, espacios y codificación se preservan. Limitación: UTF-16 se hashea byte a byte (sin equivalencia CRLF/LF; el coste es una re-extracción, nunca una reutilización errónea). `SourceArtifact.sha256` no se modificó (test sobre `evidence/builder.py`).

## 12. API final

`legacy_documenter.versions`: `ANALYZER_VERSION`, `LEGACY_MARKDOWN_RENDERER_VERSION`, `evidence_schema_version()`, `renderer_versions()`.
`legacy_documenter.fingerprints`: `analyzer_code_fingerprint`, `CodeFingerprint`, `analysis_config_fingerprint`, `projection_config_fingerprint`, `config_fingerprint`, `template_profile_fingerprint`, `semantic_content_sha256`, `semantic_file_sha256`, `CLI_OPTION_CLASSES`, `V52_PARAMETER_CLASSES`, constantes de clase, `ANALYZED_FILE_TYPES`.

Mantenibilidad: una primera versión monolítica (`fingerprints.py`, 300 líneas) midió **VERY_HIGH** (6 responsabilidades) con la herramienta del inventario; se dividió por responsabilidad. Resultado: 6 módulos LOW + `code.py` MEDIUM (89 líneas); sin ciclos.

## 13. Tests dirigidos (55 nuevos)

Versiones (6): tipo estable, schema reutilizado, familias, mapa congelado, nada del runtime los consume, independencia de runtime. Code fingerprint (16): mismo árbol, orden, extractor/analysis/scanner/models/sanitizer/config incluidos, solo funciones listadas de `pipeline_stages`, ficheros fuera de alcance, mtimes, CRLF, ilegible/ausente, solo-pyc, función ausente, no parseable, rutas normalizadas. Config (9) y CLI (4). Template/profile (10). Hash semántico (11). Guardián (§14).

## 14. Guardián de versión

`test_analyzer_version_guard`: el par `(GUARD_ANALYZER_VERSION=1, GUARD_ANALYZER_CODE_FINGERPRINT=81168845…)` vive **en el test**, no en runtime. Si el código relevante cambia y `ANALYZER_VERSION` sigue igual, falla con mensaje que indica subir la versión y actualizar ambos valores (imprime el fingerprint nuevo); si la versión se sube sin actualizar el par, también falla. Actualizarlo exige intención explícita; no se autoactualiza.

## 15. Suite completa

`python -m unittest discover -s tests`: **2 561 tests, 0 fallas, 0 errores, 132 skips**, 237 s (2 506 previas + 55 nuevas).

## 16. Validación IST

Sin corrida de pipeline completa: la ronda no toca ejecución (ningún módulo existente de producción cambió y nada consume lo nuevo). Validación controlada sobre `C:\Users\cgalianj\source\IST_40\Operacional` (15 138 archivos escaneados; 8 106 de tipos analizados: 4 328 `vb_source`, 3 165 `ascx`, 259 `vb_project`, 177 `aspx`, 113 `solution`, 60 `web_config`, 4 `master`): fingerprints calculables y deterministas (dos cálculos idénticos; combinación de `--exclude` en otro orden igual); 8 106 hashes semánticos, ninguno `None`, idénticos en dos pasadas; tipos no analizados devuelven `None`.

## 17. Costes medidos

| Cálculo | Tiempo |
|---|---:|
| `ANALYZER_CODE_FINGERPRINT` | 0,015 s |
| análisis config | < 1 ms |
| template/profile fingerprint | 0,006 s |
| projection/config fingerprint (incluye el anterior) | 0,007 s |
| hash semántico, 8 106 archivos (102,7 MB), lectura en frío | 15,0 s |
| ídem en caliente | 3,8 s (SHA-256 crudo de los mismos archivos: 4,2 s) |

Memoria: pico Python 2,7 MB (se procesa archivo a archivo). 8 105 de los 8 106 archivos analizados contienen CR (la normalización es relevante). El coste en frío es lectura de disco/antivirus, que ya se paga hoy en la extracción; R1 prevé una sola lectura por archivo.

## 18. Deuda técnica

| Hallazgo | Clase |
|---|---|
| El código fingerprint no incluye `evidence/` (la evidencia derivada está cubierta por `EVIDENCE_SCHEMA_VERSION`, no por fingerprint de código); revisar al cachear evidencia | FUTURE_PHASE |
| D-15 de R1 (renderers sin mecanismo que obligue a subir su versión): esta ronda registra las versiones pero **no** añade guardián por fingerprint para renderers; R1 lo condiciona a usarlas como claves | NEXT_ROUND / FUTURE_PHASE |
| `analysis/` completo entra al fingerprint (incluye `deep_*`, `targeted_exhaustion`): conservador, puede invalidar por cambios que no afectan extracción | OBSERVATION |
| Distribución solo `.pyc`: fingerprint `unavailable` (comportamiento previsto; la caché futura debe desactivarse) | OBSERVATION |
| Sexta clase `repository-identity` fuera de la lista del prompt | OBSERVATION (decisión a confirmar) |
| Clasificación de parámetros de biblioteca de v52 (`V52_PARAMETER_CLASSES`) no está ligada a ninguna opción CLI | OBSERVATION |
| Coste en frío del hash semántico (15 s) depende de I/O | OBSERVATION |
| BLOCKING / CURRENT_PHASE | ninguno |

## 19. Riesgos

Olvidar subir `ANALYZER_VERSION`: mitigado por fingerprint + guardián (el guardián solo protege el árbol de desarrollo; en runtime el fingerprint por sí solo ya invalida). Fingerprint demasiado estrecho: cambios en `evidence/` o `utils/` distintos del sanitizer no entran (ver deuda). Demasiado ancho: `analysis/` y `models/` completos. Acoplamiento con el parser: la clasificación se contrasta contra el parser real, no lo duplica.

## 20. Fuera de alcance confirmado

No se inició R2.4; sin File State, `_cache_v53/`, `CACHE_MANIFEST.json`, extraction cache, cambios en Evidence Core, IDs, manifests, CLI ni flujo de ejecución; sin IA; sin commit/tag/push; `PROJECT_STATE.json` intacto.

## 21. Estado Git (solo consultas)

Rama `main`, HEAD `6c32c4c` (tag `v5.2`). Modificados: `cli/full_pipeline.py`, `cli/parser.py`, `cli/pipeline_stages.py`, `cli/router.py`, `context/hydration.py`, `documentation_v52/engine.py`, `tests/test_v4_1_r0_maintainability_inventory.py`. Nuevos de producción: `context/hydration_view.py`, `documentation_v52/writer.py`, `utils/path_limits.py`, `versions.py`, `fingerprints/`. Tests nuevos: `test_v5_3_r2_1_*`, `test_v5_3_r2_2_*`, `test_v5_3_r2_3_*`. Pendientes previos: cambios sin commit de R2.1, R2.2, R2.2.1 y documentos/prompts de V5.3.

## 22. Estado final

Fingerprints deterministas, clasificación de CLI completa y verificada contra el parser real, 2 561 tests verdes, comportamiento del pipeline sin cambios, costes razonables.

**V5_3_R2_3_READY_FOR_REVIEW**
