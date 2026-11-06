# LegacyMapper V5.3 — R2.9.1 Git Checkpoint

## 1. Objetivo

Crear un único commit local con todos los cambios aprobados de R2.9:

- comparador full vs incremental;
- herramienta de calibración;
- tests R2.9;
- informe Markdown y JSON de calibración;
- `PROJECT_STATE.json`;
- documentos de continuidad;
- `.gitignore` ajustado para outputs locales de R2.9;
- informe pendiente de R2.8.2;
- prompt de R2.9.

Esta ronda es administrativa.

NO iniciar R3.

## 2. Estado de partida

Según R2.9 aprobado humanamente:

- rama: `main`;
- HEAD: `c5f70143193b55713e3ca3d67bffaa7d997c9227`;
- `main` está 5 commits por delante de `origin/main`;
- backup:
  `backup/v5.3-pre-worktree-cleanup`
  → `2cb317fe5ae3dd2cbad1f865b1faee4a50a99569`;
- R2.9:
  `V5_3_R2_9_READY_FOR_REVIEW`;
- estado adicional:
  `CHANGED_RATIO_DEFAULT_DEFERRED`;
- aprobación humana concedida;
- defaults aprobados para V5.3:
  - `cache-mode=auto`
  - `verify-cache=fast`
  - `trust-mtime=false`
  - `incremental-max-changed-ratio=None`
- R2 completo técnicamente;
- V5.3 todavía abierta;
- R3 no iniciado.

## 3. Autorización

Autorizado:

- consultas Git;
- validaciones dirigidas;
- staging explícito;
- crear UN commit local.

NO autorizado:

- push;
- tag;
- release;
- amend;
- rebase;
- reset destructivo;
- clean;
- force push;
- iniciar R3.

## 4. Fuentes obligatorias

Leer antes de actuar:

- `docs/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.md`
- `docs/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.json`
- `docs/V5/V5_3_R2_8_2_GIT_CHECKPOINT.md`
- `prompts/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.md`
- `PROJECT_STATE.json`
- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`
- `AGENTS.md`
- `CLAUDE.md`

## 5. Verificación pre-commit

Ejecutar:

- `git status --short`
- `git diff --stat`
- `git diff --check`
- revisar diff completo de código/dev-tools/docs
- confirmar rama
- confirmar HEAD
- confirmar backup branch

Verificar que NO entren:

- `output/v53r29/`;
- copias de IST;
- caches;
- PLAN/runs temporales;
- outputs de calibración pesados;
- `__pycache__/`;
- `.claude/`;
- `.tmp`;
- backups externos;
- artefactos accidentales.

No usar `git add .` sin revisión.

## 6. Archivos esperados

Esperados según R2.9:

### Herramientas

- `tools/v5_3_compare_full_incremental.py`
- `tools/v5_3_r2_9_calibrate.py`

### Tests

- `tests/test_v5_3_r2_9_incremental_calibration.py`

### Estado / continuidad

- `PROJECT_STATE.json`
- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`

### Documentación R2.9

- `docs/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.md`
- `docs/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.json`
- `prompts/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.md`

### Pendiente anterior

- `docs/V5/V5_3_R2_8_2_GIT_CHECKPOINT.md`

### Repo hygiene

- `.gitignore`

Si aparecen archivos adicionales, detenerse y clasificarlos antes de staging.

## 7. Validaciones mínimas

Ejecutar:

`python -m unittest tests.test_v5_3_r2_9_incremental_calibration`

y:

`git diff --check`

No repetir IST ni la suite completa: R2.9 ya ejecutó:

- 2 834 tests;
- 0 fallas;
- 0 errores;
- 132 skips;
- 33 corridas manuales;
- 21 comparaciones equivalentes.

Si aparece cualquier cambio nuevo en runtime/cache no documentado en R2.9:

- NO hacer commit todavía;
- ejecutar suite completa;
- documentar la causa.

## 8. Confirmaciones funcionales antes del commit

Verificar que los cambios versionados NO alteran runtime/cache.

Debe seguir vigente:

- `cache-mode=auto`;
- `verify-cache=fast`;
- `trust-mtime=false`;
- `incremental-max-changed-ratio=None`;
- changed ratio diferido;
- comparador en `tools/`, no importado por runtime;
- calibrador en `tools/`, no importado por runtime;
- R3 no iniciado;
- V5.3 no cerrada.

## 9. Staging

Agregar por rutas explícitas.

Después:

`git diff --cached --stat`

`git diff --cached`

Confirmar que el staging contiene exclusivamente:

- R2.9;
- informe pendiente R2.8.2;
- continuidad;
- `.gitignore`.

## 10. Commit

Crear UN commit local.

Mensaje recomendado:

`chore(v5.3): checkpoint incremental calibration`

Alternativa aceptable si el repo prefiere `feat`:

`feat(v5.3): add incremental calibration and comparison tooling`

Elegir uno y documentar la razón.

No amend.

## 11. Post-commit

Registrar:

- hash completo;
- hash corto;
- padre;
- rama;
- `git log -1 --oneline`;
- commits ahead de `origin/main`;
- backup intacto;
- `git status --short`.

Esperado:

- working tree limpio salvo el informe de esta ronda.

## 12. Documento de esta ronda

Crear:

`docs/V5/V5_3_R2_9_1_GIT_CHECKPOINT.md`

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
11. Defaults V5.3 aprobados.
12. R2 técnicamente completo.
13. Pendientes.
14. Recomendación para R3.
15. Estado final.

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

`V5_3_R2_9_1_CHECKPOINT_CREATED`

Si hay archivos inesperados, tests fallan o el staging no es seguro:

`V5_3_R2_9_1_BLOCKED`

## 16. Criterio de cierre

La ronda termina si:

- R2.9 queda versionada;
- R2.8.2 queda incluida;
- continuidad queda versionada;
- no hubo push/tag;
- test dirigido verde;
- Git coherente;
- hash documentado;
- R3 puede iniciar desde el nuevo commit.

Detenerse para revisión humana.
