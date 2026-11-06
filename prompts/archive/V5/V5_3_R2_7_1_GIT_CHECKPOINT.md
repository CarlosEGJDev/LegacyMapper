# LegacyMapper V5.3 — R2.7.1 Checkpoint Git de R2.7

## 1. Objetivo
Versionar en un commit local propio los cambios validados de V5.3 R2.7, incluyendo scope analysis, persisted run metrics, tests, prompt, documento de resultado y el documento pendiente de R2.6.1. Esta ronda es exclusivamente administrativa. NO iniciar R2.8.

## 2. Estado de partida
Según `docs/V5/V5_3_R2_7_SCOPE_ANALYSIS_AND_RUN_METRICS.md`: rama `main`, HEAD `c49a8a4`, `main` 3 commits por delante de `origin/main`, rama `backup/v5.3-pre-worktree-cleanup`, R2.7 `V5_3_R2_7_READY_FOR_REVIEW`, suite 2 744 tests, 0 fallas, 0 errores, 132 skips, sin commit/tag/push de R2.7. Sigue pendiente `docs/V5/V5_3_R2_6_1_GIT_CHECKPOINT.md`.

## 3. Autorización
Autorizado: revisar Git, ejecutar validaciones, staging explícito y crear UN commit local.
No autorizado: push, tag, release, amend, rebase, reset destructivo, clean, force push, iniciar R2.8.

## 4. Fuentes obligatorias
Leer:
- `docs/V5/V5_3_R2_7_SCOPE_ANALYSIS_AND_RUN_METRICS.md`
- `prompts/V5/V5_3_R2_7_SCOPE_ANALYSIS_AND_RUN_METRICS.md`
- `docs/V5/V5_3_R2_6_1_GIT_CHECKPOINT.md`
- `docs/V5/V5_3_R2_6_WRITE_SKIP_REMAINING_OUTPUTS.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

## 5. Observación contractual a preservar
- `archivo → proyecto` está dentro del contrato.
- El cierre transitivo de dependientes se usa solo como suelo conocido/observabilidad.
- NO convertirlo en invalidación parcial o stage skipping.
- Cambios de código/`.vbproj`/`.sln` siguen siendo conservadores/full cuando corresponda.

## 6. Verificación pre-commit
Ejecutar `git status --short`, `git diff --stat`, revisar modificados/nuevos, confirmar rama/HEAD/backup y verificar que no haya outputs de medición, `_cache_v53/`, `RUN_METRICS.json` generado, `.tmp`, `__pycache__/`, `.claude/`, backups externos ni archivos inesperados. No usar `git add .` sin revisar.

## 7. Archivos esperados
Código:
- `legacy_documenter/cache/scope.py`
- `legacy_documenter/cache/run_metrics.py`
- `legacy_documenter/cache/run_report.py`
- `legacy_documenter/utils/stage_timings.py`
- `legacy_documenter/cache/session.py`
- `legacy_documenter/cache/__init__.py`
- `legacy_documenter/cli/full_pipeline.py`
- `legacy_documenter/cli/pipeline_stages.py`

Tests:
- `tests/test_v5_3_r2_7_scope_and_run_metrics.py`
- ajustes de inventario, R2.2, R2.4 y R2.6.

Documentación:
- `prompts/V5/V5_3_R2_7_SCOPE_ANALYSIS_AND_RUN_METRICS.md`
- `docs/V5/V5_3_R2_7_SCOPE_ANALYSIS_AND_RUN_METRICS.md`
- `docs/V5/V5_3_R2_6_1_GIT_CHECKPOINT.md`

## 8. Verificación de contenido
Confirmar:
- `RUN_METRICS.json` fuera de outputs de producto;
- métricas no participan de hashes/cache validity;
- scope no gobierna stages;
- resolvers y proyecciones siguen recomputándose;
- `artifacts.json` NO existe;
- `ARTIFACT_STATE_DEFERRED_BY_CONTRACT` sigue vigente;
- no hay nuevos controles CLI;
- no hay cambios en IDs/Evidence Core;
- no hay cambios ajenos a R2.7.

## 9. Tests
Ejecutar tests dirigidos de R2.7, tests relacionados de R2.6 y `git diff --check`. Si falla algo: NO commit y estado BLOCKED. No es obligatorio repetir suite completa si no hubo cambios posteriores.

## 10. Staging
Agregar por rutas explícitas. Revisar `git diff --cached --stat` y `git diff --cached`. Debe contener solo R2.7, el documento pendiente R2.6.1 y documentación asociada.

## 11. Commit
Crear un único commit local:
`feat(v5.3): add scope analysis and run metrics`
Sin amend.

## 12. Post-commit
Registrar hash completo/corto, padre, rama, `git status --short`, `git log -1 --oneline`, commits por delante de `origin/main` y rama backup intacta.

## 13. Entregable
Crear `docs/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md` con:
1. Objetivo
2. Estado inicial
3. Archivos versionados
4. Validaciones
5. Tests
6. Staging
7. Commit
8. Hash
9. Estado post-commit
10. Confirmación no push/no tag
11. Archivos pendientes
12. Recomendación para R2.8
13. Estado final

## 14. Documento posterior al commit
Como contiene el hash del commit, puede quedar sin versionar. NO crear segundo commit solo para incluirlo.

## 15. Git prohibido
No push, tag, amend, rebase, reset --hard, clean, branch -D ni force push.

## 16. Estado final permitido
Si el commit se crea: `V5_3_R2_7_1_CHECKPOINT_CREATED`
Si hay problemas: `V5_3_R2_7_1_BLOCKED`

## 17. Criterio de cierre
R2.7 versionado en commit local; documento R2.6.1 incluido; no push/tag; tests dirigidos verdes; Git coherente; hash documentado; R2.8 puede iniciar desde ese commit. Detenerse para revisión humana.
