# V5.3 R2.8.1 — VERIFY_CACHE_BARE_FIX

Fecha: 2026-10-05. Estado: **V5_3_R2_8_1_READY_FOR_REVIEW**.

## Defecto / causa / solución

- Defecto R2.8: bare `--verify-cache` antes del repositorio podía consumirlo como valor, incluso si la ruta se llamaba `fast` o `hash`.
- Causa: `argparse`, `nargs="?"`, choices `fast/hash`; `const="hash"` no impide consumir un token siguiente.
- Solución CLI: `normalize_cache_argv` convierte el token exacto en `--verify-cache=hash`, sin mirar el siguiente. `_CacheArgumentParser.parse_known_args` aplica la normalización antes del parsing tanto en `main()` como en `build_parser().parse_args(...)`. Subparsers estándar evitan renormalizar posicionales. Helper conserva orden, lista original y tokens similares; es idempotente, sin filesystem, y respeta `--`.

## Archivos de esta ronda

- Modificado: `legacy_documenter/cli/parser.py` (helper, parser, ayuda).
- Nuevo: `tests/test_v5_3_r2_8_1_verify_cache_bare_fix.py`.
- Actualizado: `docs/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`, únicamente §8 y §30.
- Nuevo: este reporte en `codex/`, conforme a AGENTS.md; entrada documental `docs/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md` enlaza el reporte.

## Semántica final

| Entrada | Resultado |
|---|---|
| ausente | `fast` |
| bare, antes/después de repository o antes de otro flag | `hash`, siguiente argumento intacto |
| `--verify-cache=hash` | `hash` |
| `--verify-cache=fast` | `fast` |
| `--verify-cache=foo` | parser exit 2, `invalid choice` |
| repository `hash`, `fast`, ruta con espacios o texto similar | repository intacto |
| `--` seguido por ruta llamada `--verify-cache` | ruta literal intacta |
| `analyze` + cualquiera de las tres formas válidas | parser exit 2; control exclusivo de `full` |

`full` admite un solo posicional (`repository`); caso «entre posicionales» no aplicable. Probado entre repository y `--output`, conservando ambos valores. Niveles explícitos usan `=`; un token separado después del bare nunca se interpreta como nivel.

## Tests / smoke

15 tests nuevos: defaults, posiciones bare, niveles explícitos, inválido con diagnóstico/exit code, rutas `hash`/`fast`/espacios, rechazo de analyze, helper exacto/no mutación/orden/idempotencia, end-of-options, `sys.argv`, router 1:1 y smoke.

Smoke A–D: procesos Python reales ejecutan `main.py` mediante `runpy`, usando `tests/fixtures/v4_2_r7_full_sample` y `--output output/v5_3_r2_8_1_smoke`. Solo se intercepta `router.run_full_pipeline` y la presentación de consola. No se escribe esa salida ni se analiza IST.

| Caso | argv después de main.py | mapping observado |
|---|---|---|
| A | `full <repo> --output <out> --verify-cache` | repository/output intactos; `hash`; exit 0 |
| B | `full --verify-cache <repo> --output <out>` | repository/output intactos; `hash`; exit 0 |
| C | `full <repo> --output <out> --verify-cache=fast` | `fast`; exit 0 |
| D | `full <repo> --output <out> --verify-cache=hash` | `hash`; exit 0 |

Todos verifican `allow_ai_interpretation=false`.

Comando dirigido corregido:

```text
python -m unittest tests.test_v4_2_r1_cli_contract_and_execution_model tests.test_v4_2_r5_unified_cli_and_operational_ux tests.test_v5_3_r2_2_write_skip_and_max_path.CliLongPathsOptionTests tests.test_v5_3_r2_3_versioning_and_fingerprints tests.test_v5_3_r2_8_1_verify_cache_bare_fix
```

Resultado: 136 tests, OK, 36.644 s. La ejecución inicial seleccionó por error `CliTests` (clase inexistente): 190 entradas, 0 failures y 1 loader error. Corregido a `CliLongPathsOptionTests`; 3 tests también pasaron por separado. No defecto del producto.

Regresión R2.8 independiente:

```text
python -m unittest tests.test_v5_3_r2_8_cache_cli_controls
```

Resultado: 56 tests, OK, 103.424 s. Total dirigido final: **192 tests, 0 failures, 0 errors, 0 skips** (136 + 56; los 3 tests aislados son repetición). Smoke A–D incluidos en el test nuevo: 4/4 correctos.

`git diff --check`: exit 0; sin errores de whitespace. Check adicional del test nuevo (`git diff --no-index --check -- /dev/null tests/test_v5_3_r2_8_1_verify_cache_bare_fix.py`): sin errores. Avisos Git de conversión LF→CRLF preexistentes, sin alterar configuración.

## Alcance / impacto

Runtime/cache no modificado por R2.8.1: `cache/verify.py`, algoritmos fast/hash, fallback, File State, extraction cache, scope, write-skip, parámetros de biblioteca y router permanecen como al inicio. Los cambios preexistentes de R2.8 siguen sin versionar y no se atribuyen a esta corrección. Default `fast` y mapping 1:1 conservados.

Informe R2.8: deuda del bare eliminada; normalización inequívoca registrada. Restantes conclusiones, riesgos y mediciones IST A–H conservados. Sin repetir IST ni suite completa: cambio estrictamente parser/tests/docs. Sin R2.9, cambios al contrato R1, llamadas IA ni cambios al legacy.

## Git / continuidad

- Solo consultas Git; sin commit, push, tag, amend, rebase, reset o clean.
- Rama `main`; HEAD `dae2ba5083bf3c6f863106456e201f0c4e55ab42`; 4 commits por delante de `origin/main`.
- Modificados preexistentes: `cache/{__init__,file_state,run_metrics,run_report,session}.py`, `cli/{full_pipeline,parser,router}.py`, `documentation_v52/writer.py`, `fingerprints/configuration.py`, `utils/write_if_changed.py`, `tests/test_v4_1_r0_maintainability_inventory.py` (todos los módulos bajo `legacy_documenter/`). Solo parser recibe edición adicional de esta ronda.
- Nuevos preexistentes: `legacy_documenter/cache/{options,verify}.py`, `legacy_documenter/utils/write_policy.py`, `tests/test_v5_3_r2_8_cache_cli_controls.py`, `docs/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`, `prompts/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`, `prompts/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md`.
- Pendientes documentales R2.7.1: `prompts/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`, `docs/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`.
- Nuevos de R2.8.1: test, reporte codex y entrada docs listados arriba. Informe R2.8 actualizado continúa untracked.
- `PROJECT_STATE.json` permanece en R2.5.1/next R2.6, discrepancia preexistente documentada por R2.8 §33. No actualizado: esta ronda no solicita checkpoint/cierre; ejecución limitada a la instrucción explícita R2.8.1.

## Estado final

**V5_3_R2_8_1_READY_FOR_REVIEW**. Corrección y validación completas; detenido para revisión humana. R2.9 no iniciada.
