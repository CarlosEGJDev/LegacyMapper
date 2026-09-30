# V5.2 R4.2 — Correcciones acotadas antes del cierre

## 1. Objetivo

Resolver dos deudas evitables identificadas en R4.1: (A) falta de pruebas directas de `_replace_with_retry` y (B) ambigüedad del texto «N archivos de código» frente a la tabla de archivos. Sin rediseño, sin V5.3, sin cambios al Evidence Core.

Decisión humana registrada: baseline oficial de V5.2 = `C:\Users\cgalianj\source\IST_40\Operacional`.

## 2. Estado inicial de Git observado

`git status` al inicio: 26 entradas, idénticas a las de R4.1 (12 modificadas/borradas: `CLAUDE.md`, 3 documentos de continuidad, `pipeline_stages.py`, `run_summary_presenter.py`, `atomic_write.py`, 4 tests históricos, borrado `docs/V5_0/V5_0_R0_…PROMPT.md`; y rutas sin seguimiento de V5). Se preservaron todas. Al final, la única diferencia respecto a ese estado es el test nuevo (y este informe, más los archivos de la sección 3).

## 3. Archivos modificados o creados

| Archivo | Cambio |
|---|---|
| `legacy_documenter/documentation_v52/defaults/i18n/es.json` | Solo el texto de la clave `dev.module.own_text` (presentación). |
| `tests/test_v5_2_r4_2_pre_closure_corrections.py` | **Nuevo**: 8 tests. |
| `docs/V5/V5_2_R4_2_CORRECCIONES_PRE_CIERRE.md` | Este informe. |

No se modificó `atomic_write.py` ni ningún otro código de producción. Fuera del repositorio: regeneración en `C:\PruebasLegacyMapper\Resultados\v5_2_r4_2_regen\` (la salida persistida de R3.4.1 no se tocó).

## 4. Corrección A — pruebas de `_replace_with_retry`

Se simulan `os.replace` y `time.sleep` (sin esperas reales, deterministas). Casos:

1. Primer intento con `PermissionError` y segundo con éxito: 2 llamadas, un solo `sleep` con el retardo inicial.
2. Todos los intentos fallan: se relanza `PermissionError` tras 5 intentos; los retardos son 4 y crecen al doble (backoff).
3. Excepción distinta (`OSError`): 1 intento, sin `sleep`.
4. Éxito inmediato: sin `sleep`.
5. Integración con `atomic_write_text`, fallo transitorio: el contenido se escribe y no queda archivo temporal.
6. Integración, reintentos agotados: se conserva el archivo original y se elimina el temporal.

No hizo falta cambiar la política ni el código: el comportamiento existente era plenamente comprobable.

## 5. Corrección B — texto ambiguo

Causa (R3.3 §11.3): «declara N archivos de código» cuenta solo `compile_items` (`Project -> SourceFile`), mientras la tabla «Componentes y archivos» incluye también `content_items` (`.aspx`, `.ascx`, `.master` y otros recursos).

Texto nuevo (solo i18n, sin tocar renderer, transformación ni conteos):

> El proyecto declara {source_files} archivos de código compilables (por ejemplo .vb o .cs). La tabla «Componentes y archivos» de más abajo puede tener más filas porque también incluye los archivos de contenido declarados (.aspx, .ascx, .master y otros recursos). Sus puntos de entrada propios son {screens} pantallas con {events} eventos.

Tests (2 de los 8 nuevos): el catálogo contiene los rótulos que distinguen ambos conteos y el documento generado del proyecto `BLInterfazSAP` muestra el texto aclarado. El texto a nivel de sistema («archivos de código fuente», General Overview) no se cambió: no forma parte de la ambigüedad.

## 6. Validaciones dirigidas

Siete módulos V5 (R2, R3.1, R3.2, R3.3, R3.4, R3.4.1) más el módulo nuevo: **189 pruebas, OK** (15,7 s).

## 7. Regeneración desde evidencia persistida

Con `tools.v5_2_r3_4_1_method_quality_measurement` sobre `ist_full_run\evidence` (sin nueva extracción IST), salida en directorio nuevo; 7 min 27 s; 0 advertencias del renderer.

- Documentos: 46.567 `.md` (46.568 archivos con `MANIFEST.json`), **igual que antes**; mismo conjunto de rutas.
- Conteos idénticos a R3.4.1: 33.610 métodos en índice, 21.407 documentos de método, 12.203 filas solo en índice, 36 grupos ambiguos, 9.305 con acceso real, 8.309 solo transaccionales, 21.247 con expresión no resuelta visible, 2.810 con llamadas resueltas, 2.659 mixtos.
- Archivos distintos byte a byte respecto de la salida anterior: **260** = 259 documentos de proyecto (`developer/modules/<proyecto>.md`) + `MANIFEST.json`. En cada documento de proyecto difiere **una sola línea** (el párrafo aclarado). Ningún otro documento cambió.
- Bytes totales: 59.152.089 frente a 59.097.181 (+54.908 ≈ 212 bytes × 259), cambio esperado. Archivo máximo 52.299 bytes, sin cambio.
- Hashes del manifest cambian solo en los 259 documentos afectados.
- No se repitió la verificación de enlaces (el cambio no toca enlaces ni estructura).

## 8. Suite completa

`python -m unittest discover -s tests` (una sola ejecución, sin concurrencia): **2.449 pruebas, 0 fallas, 0 errores, 132 skips (esperados de checkout limpio), 243 s.** Coincide con 2.441 + 8 nuevas.

## 9. Contratos preservados

Sin cambios en `legacy_documenter/evidence/` ni en transformación, renderer, IDs, provenance, confidence o `unresolved` (los conteos de `unresolved` son idénticos). Compatibilidad V4.3, independencia del runtime, provider de IA opcional y separación General/Developer siguen cubiertos por los tests que pasaron en la suite; la documentación legacy no se tocó. No se ejecutó IA.

## 10. Problemas encontrados

Ninguno bloqueante. Nota: una primera versión del test de documento buscó una ruta incorrecta (`modules/<X>/README.md`); era un error del propio test, corregido a `modules/<X>.md`.

## 11. Deuda técnica restante relevante para V5.2

Sin cambios respecto de R4.1 salvo las dos resueltas aquí: continúan las de fase futura por contrato (gaps de método/firmas, code-behind, `archivo:línea`, clasificación de tipo de proyecto, GAP-M1, validación solo en IST, mantenibilidad de módulos grandes), el ruido residual `Me.X.DataBind()` (configurable) y la decisión sobre la escala documental. Pendientes de la ronda de cierre: H-1 (`PROJECT_STATE.json`/roadmap), versionado Git (H-3), convención `prompts/V5/` y corrección de las frases de R4 sobre H-2/H-4. No apareció deuda nueva que deba resolverse antes del cierre.

## 12. Estado final

**V5_2_R4_2_READY_FOR_CLOSURE_REVIEW**

No se declara `V5_2_CLOSED`.

## 13. Git

Sin commit, push, reset, checkout ni ninguna operación que cambie estado ni historial.

## 14. V5.3

No iniciada.
