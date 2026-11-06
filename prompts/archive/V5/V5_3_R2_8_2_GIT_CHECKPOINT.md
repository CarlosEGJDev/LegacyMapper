# LegacyMapper V5.3 — R2.8.2 Checkpoint Git de R2.8 + R2.8.1

## 1. Objetivo
Versionar en un único commit local la implementación completa de V5.3 R2.8, la corrección R2.8.1 de `--verify-cache` bare, tests, prompts, informes y los documentos pendientes de R2.7.1. Esta ronda es exclusivamente administrativa. NO iniciar R2.9.

## 2. Estado de partida
Según R2.8 y R2.8.1:
- rama `main`;
- HEAD `dae2ba5083bf3c6f863106456e201f0c4e55ab42`;
- `main` está 4 commits por delante de `origin/main`;
- backup `backup/v5.3-pre-worktree-cleanup`;
- R2.8 funcionalmente aprobado;
- R2.8.1 `V5_3_R2_8_1_READY_FOR_REVIEW`;
- suite R2.8: 2 800 tests, 0 fallas, 0 errores, 132 skips;
- R2.8.1: 192 tests dirigidos, 0 fallas, 0 errores;
- sin commit/tag/push de R2.8/R2.8.1.

Pendientes anteriores:
- `prompts/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`
- `docs/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`

## 3. Autorización
Autorizado:
- revisar Git;
- ejecutar validaciones;
- staging explícito;
- crear UN commit local.

No autorizado:
- push;
- tag;
- release;
- amend;
- rebase;
- reset destructivo;
- clean;
- force push;
- iniciar R2.9.

## 4. Fuentes obligatorias
Leer:
- `docs/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`
- `docs/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md`
- `codex/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md`
- `prompts/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`
- `prompts/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md`
- `docs/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`
- `prompts/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

## 5. Verificación pre-commit
Ejecutar:
- `git status --short`
- `git diff --stat`
- revisar modificados/nuevos
- confirmar rama, HEAD y backup

Verificar que NO entren:
- outputs IST;
- `_cache_v53/`;
- `RUN_METRICS.json` generado;
- `.tmp`;
- `__pycache__/`;
- `.claude/`;
- backups externos;
- outputs de smoke;
- artefactos accidentales.

No usar `git add .` sin revisión.

## 6. Archivos esperados

### Código R2.8
- `legacy_documenter/cache/__init__.py`
- `legacy_documenter/cache/file_state.py`
- `legacy_documenter/cache/run_metrics.py`
- `legacy_documenter/cache/run_report.py`
- `legacy_documenter/cache/session.py`
- `legacy_documenter/cache/options.py`
- `legacy_documenter/cache/verify.py`
- `legacy_documenter/cli/full_pipeline.py`
- `legacy_documenter/cli/parser.py`
- `legacy_documenter/cli/router.py`
- `legacy_documenter/documentation_v52/writer.py`
- `legacy_documenter/fingerprints/configuration.py`
- `legacy_documenter/utils/write_if_changed.py`
- `legacy_documenter/utils/write_policy.py`

### Tests
- `tests/test_v5_3_r2_8_cache_cli_controls.py`
- `tests/test_v5_3_r2_8_1_verify_cache_bare_fix.py`
- `tests/test_v4_1_r0_maintainability_inventory.py`
- cualquier ajuste adicional documentado explícitamente por R2.8.

### Documentación
- `prompts/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`
- `docs/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`
- `prompts/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md`
- `docs/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md`
- `codex/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md`

### Pendientes R2.7.1
- `prompts/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`
- `docs/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`

Si las rutas reales difieren, usar las del repo.

## 7. Garantías funcionales a preservar
Confirmar:
- default `cache-mode=auto`;
- `off` no lee ni escribe cache V5.3 y desactiva write-skip según R1;
- `refresh` ignora cache previa y reconstruye;
- default `verify-cache=fast`;
- bare `--verify-cache` = `hash` y no consume posicional;
- `=fast` y `=hash` funcionan;
- `hash` estricto, `fast` tolerante a un shard dañado;
- cache-dir externo seguro;
- `trust-mtime` opt-in, default false;
- changed ratio default desactivado;
- changed ratio solo provoca fallback full;
- scope sigue siendo observabilidad;
- cierre transitivo sigue siendo suelo conocido;
- `artifacts.json` no existe;
- Evidence Core/IDs sin cambios;
- no IA, no R2.9.

## 8. Validaciones
Ejecutar como mínimo:
- tests R2.8;
- tests R2.8.1;
- parser/router relacionados;
- `git diff --check`.

No hace falta repetir IST. Si aparece cualquier cambio posterior no documentado en runtime/cache, ejecutar suite completa y documentarlo.

## 9. Staging
Agregar por rutas explícitas.

Después revisar:
- `git diff --cached --stat`
- `git diff --cached`

El staging debe contener solo:
- R2.8;
- R2.8.1;
- documentos pendientes R2.7.1.

## 10. Commit
Crear UN commit local.

Mensaje recomendado:

`feat(v5.3): add cache CLI controls and verification modes`

No dividir salvo razón objetiva documentada. No amend.

## 11. Post-commit
Registrar:
- hash completo;
- hash corto;
- padre;
- rama;
- `git status --short`;
- `git log -1 --oneline`;
- commits ahead de `origin/main`;
- backup intacto.

Esperado: working tree limpio salvo el documento de esta ronda.

## 12. Documento de esta ronda
Crear:

`docs/V5/V5_3_R2_8_2_GIT_CHECKPOINT.md`

Debe incluir:
1. Objetivo.
2. Estado inicial.
3. Archivos versionados.
4. Validaciones.
5. Tests.
6. Staging.
7. Commit.
8. Hash.
9. Estado post-commit.
10. Confirmación no push/no tag.
11. Archivos pendientes.
12. Recomendación para R2.9.
13. Estado final.

## 13. Documento posterior al commit
Como contiene el hash del propio commit:
- puede quedar sin versionar;
- NO crear segundo commit solo para incluirlo;
- debe entrar en un commit posterior.

## 14. Git prohibido
No:
- push;
- tag;
- amend;
- rebase;
- reset --hard;
- clean;
- branch -D;
- force push.

## 15. Estado final permitido
Si el checkpoint queda correcto:

`V5_3_R2_8_2_CHECKPOINT_CREATED`

Si hay archivos inesperados, tests fallan o el staging no es seguro:

`V5_3_R2_8_2_BLOCKED`

## 16. Criterio de cierre
La ronda termina si:
- R2.8 + R2.8.1 quedan versionados;
- pendientes R2.7.1 quedan incluidos;
- no hubo push/tag;
- tests dirigidos verdes;
- Git coherente;
- hash documentado;
- R2.9 puede iniciar desde ese commit.

Detenerse para revisión humana.
