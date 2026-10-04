# LegacyMapper V5.3 — R2.6.1 Checkpoint Git de R2.6

## 1. Objetivo

Versionar en un commit local propio los cambios completos y validados de V5.3 R2.6:

- guardián del contrato de extraction cache;
- write-skip de salidas restantes;
- tests;
- prompt;
- documento de resultado.

Esta ronda es exclusivamente administrativa.

NO iniciar R2.7.

## 2. Estado de partida

Según `docs/V5/V5_3_R2_6_WRITE_SKIP_REMAINING_OUTPUTS.md`:

- rama: `main`;
- HEAD inicial de R2.6: `108bace`;
- rama de respaldo existente: `backup/v5.3-pre-worktree-cleanup`;
- R2.6 quedó `V5_3_R2_6_READY_FOR_REVIEW`;
- suite: 2 698 tests, 0 fallas, 0 errores, 132 skips;
- no hubo commit, tag ni push de R2.6.

## 3. Autorización

El usuario autorizó continuar.

Queda autorizado:

- revisar Git;
- ejecutar validaciones;
- hacer staging explícito de los archivos de R2.6;
- crear UN commit local de R2.6.

NO queda autorizado:

- push;
- tag;
- release;
- amend;
- rebase;
- reset destructivo;
- clean;
- force push;
- iniciar R2.7.

## 4. Fuentes obligatorias

Leer antes de actuar:

- `docs/V5/V5_3_R2_6_WRITE_SKIP_REMAINING_OUTPUTS.md`
- `prompts/V5/V5_3_R2_6_WRITE_SKIP_REMAINING_OUTPUTS.md`
- `docs/V5/V5_3_R2_5_4_BACKUP_AND_WORKTREE_CLEANUP.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

## 5. Verificación pre-commit

Ejecutar:

- `git status --short`
- `git diff --stat`
- revisar archivos modificados/nuevos
- verificar rama actual
- verificar HEAD
- verificar que no hay:
  - outputs de medición;
  - `_cache_v53/`;
  - `.tmp`;
  - `__pycache__/`;
  - `.claude/`;
  - backups externos;
  - archivos inesperados.

No usar `git add .` sin revisar.

## 6. Archivos esperados de R2.6

Según el informe, revisar y versionar los cambios relevantes en:

- `legacy_documenter/utils/write_if_changed.py`
- `legacy_documenter/fingerprints/extraction_contract.py`
- `legacy_documenter/fingerprints/__init__.py`
- `legacy_documenter/versions.py`
- `legacy_documenter/cache/context.py`
- `legacy_documenter/cache/manifest.py`
- `legacy_documenter/cache/extraction.py`
- `legacy_documenter/cache/extraction_store.py`
- `legacy_documenter/exporters/json_exporter.py`
- `legacy_documenter/evidence/persistence.py`
- `legacy_documenter/exporters/markdown_exporter.py`
- `legacy_documenter/context/context_builder.py`
- `legacy_documenter/context/system_context_builder.py`
- `legacy_documenter/cli/artifact_lifecycle.py`
- `legacy_documenter/cli/pipeline_stages.py`
- `legacy_documenter/cli/full_pipeline.py`
- `tests/test_v5_3_r2_6_write_skip_and_extraction_guardian.py`
- ajustes de tests R2.4 / inventario de mantenibilidad
- prompt R2.6
- documento de resultado R2.6

Si el path real del paquete difiere, usar las rutas reales del repo.

## 7. Verificación de contenido

Antes del staging:

Confirmar que:

- no hay cambios funcionales ajenos a R2.6;
- `EXTRACTION_CACHE_SCHEMA_VERSION` está presente;
- el guardián tiene su fingerprint;
- write-skip usa comparación de bytes;
- `documentation_v52` no fue reimplementado;
- `RUN_SUMMARY` no cambió;
- no hay nuevos controles CLI;
- no hay cambios en IDs/Evidence Core;
- no hay archivos generados accidentalmente.

## 8. Tests

Como R2.6 ya reportó suite completa verde:

- ejecutar al menos los tests dirigidos de R2.6;
- ejecutar `git diff --check`.

Si cualquier test dirigido falla:

- NO commit;
- estado BLOCKED.

La suite completa puede repetirse si el agente detecta alguna diferencia respecto del resultado reportado o cambios posteriores a la medición.

## 9. Staging

Agregar por rutas explícitas.

Después:

- `git diff --cached --stat`
- revisar `git diff --cached`

Confirmar que el staging contiene SOLO R2.6 y su documentación.

## 10. Commit

Crear un único commit local.

Mensaje recomendado:

`feat(v5.3): add extraction cache guard and output write-skip`

No dividir salvo razón objetiva documentada.

No hacer amend.

## 11. Post-commit

Registrar:

- hash completo;
- hash corto;
- padre;
- rama;
- `git status --short`;
- `git log -1 --oneline`;
- relación con `origin/main`.

Esperado:

- `main` por delante de `origin/main`;
- R2.6 ya versionado;
- working tree limpio, salvo documentos de esta ronda que naturalmente se creen después del commit.

## 12. Documento de esta ronda

Crear:

`docs/V5/V5_3_R2_6_1_GIT_CHECKPOINT.md`

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
11. Archivos pendientes si los hay.
12. Recomendación para R2.7.
13. Estado final.

## 13. Documento posterior al commit

Como este documento contiene el hash del commit, puede quedar sin versionar.

NO crear un segundo commit en esta ronda solo para incluirlo.

Debe registrarse explícitamente para incorporarlo en un commit posterior.

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

Si el commit se crea correctamente:

`V5_3_R2_6_1_CHECKPOINT_CREATED`

Si hay archivos inesperados, tests fallan o el staging no puede garantizarse:

`V5_3_R2_6_1_BLOCKED`

## 16. Criterio de cierre

La ronda termina si:

- R2.6 quedó versionado en un commit local;
- no hubo push ni tag;
- el commit contiene solo cambios de R2.6;
- los tests dirigidos están verdes;
- Git queda coherente;
- el hash queda documentado;
- R2.7 puede empezar desde ese commit.

Detenerse para revisión humana.
