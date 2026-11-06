# LegacyMapper V5.3 — R2.5.2 Continuidad, limpieza Git y checkpoint

## 1. Objetivo

Cerrar la higiene detectada en R2.5.1 antes de iniciar R2.6.

Esta ronda debe:

1. actualizar el estado y continuidad documental para reflejar la realidad actual;
2. revisar y, si es seguro, retirar los worktrees residuales de agentes;
3. consolidar el trabajo V5.3 realizado desde R0 hasta R2.5.1 en un commit checkpoint local;
4. dejar el repositorio en un estado coherente y recuperable.

NO iniciar R2.6.

## 2. Autorización humana

El usuario autorizó explícitamente continuar con esta ronda administrativa.

Queda autorizado:

- modificar `PROJECT_STATE.json`;
- modificar documentos de continuidad vigentes;
- retirar worktrees residuales SOLO si están limpios y sus commits ya están integrados;
- eliminar sus ramas locales asociadas SOLO si están totalmente integradas y no contienen trabajo exclusivo;
- crear un commit checkpoint local de V5.3.

NO queda autorizado:

- push;
- tag;
- release;
- force push;
- rebase destructivo;
- reset destructivo;
- borrar trabajo no integrado;
- iniciar R2.6.

## 3. Fuentes obligatorias

Leer antes de actuar:

- `docs/V5/V5_3_R2_5_1_REPOSITORY_HYGIENE_AUDIT.md`
- `docs/V5/V5_3_R2_5_EXTRACTION_CACHE.md`
- `docs/V5/V5_3_R2_4_CACHE_MANIFEST_AND_FILE_STATE.md`
- `docs/V5/V5_3_R2_3_VERSIONING_AND_FINGERPRINTS.md`
- `docs/V5/V5_3_R2_2_1_MAINTAINABILITY_AND_FINAL_VALIDATION.md`
- `docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md`
- `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`
- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_2_GIT_CLOSURE_RESULT.md`
- `PROJECT_STATE.json`
- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`
- `AGENTS.md`
- `CLAUDE.md`

## 4. Estado que debe reflejarse

Actualizar continuidad vigente para que quede claro:

- V5.2 está cerrada;
- commit de cierre V5.2: `6c32c4c...`;
- tag `v5.2`;
- V5.2 ya no está pendiente de aprobación Git;
- V5.3 está iniciada;
- rondas completadas:
  - R0;
  - R0.1;
  - R1;
  - R2.1;
  - R2.2;
  - R2.2.1;
  - R2.3;
  - R2.4;
  - R2.5;
  - R2.5.1;
- estado actual: preparación para R2.6;
- última suite conocida: 2.663 tests, 0 fallas, 0 errores, 132 skips;
- extraction cache adoptada;
- no existe cierre ni tag V5.3 todavía.

No reescribir narrativa histórica de rondas pasadas.

## 5. PROJECT_STATE.json

Actualizar únicamente los campos vigentes que estén claramente desactualizados.

Debe reflejar como mínimo:

- versión actual V5.3;
- `v5_3_started = true` o equivalente existente;
- cierre Git de V5.2 resuelto;
- última ronda completada = R2.5.1;
- siguiente paso = R2.6;
- suite actual = 2.663 tests;
- sin declarar V5.3 cerrada;
- sin declarar tag V5.3.

Mantener compatibilidad con el esquema existente.

Validar JSON al terminar.

## 6. Roadmap y continuidad

Actualizar solo secciones vigentes de:

- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`

Objetivo:

- eliminar afirmaciones vigentes falsas como “V5.2 pendiente de Git”;
- marcar V5.3 como en curso;
- registrar avance hasta R2.5.1;
- conservar intactas las afirmaciones históricas cuando describen el estado real de una ronda pasada.

No reescribir documentos históricos de cierre de V5.2.

## 7. Worktrees residuales

R2.5.1 detectó dos worktrees:

- `.claude/worktrees/agent-a00511fc…`
- `.claude/worktrees/agent-a0c75b43…`

Antes de eliminarlos:

1. ejecutar `git worktree list --porcelain`;
2. identificar la rama de cada worktree;
3. verificar `git status --short` dentro de cada worktree;
4. verificar que no hay archivos sin seguimiento relevantes;
5. verificar que el commit de la rama está contenido en `main`:
   - `git merge-base --is-ancestor <branch-or-commit> main`
6. verificar que no hay commits exclusivos:
   - comparar `main..<branch>`;
7. si hay cualquier diferencia, NO eliminar y marcar `NEEDS_HUMAN_DECISION`.

Solo si todo está limpio e integrado:

- `git worktree remove <path>`;
- eliminar la rama local asociada con borrado seguro (`git branch -d`, NO `-D`);
- ejecutar `git worktree prune`.

Registrar exactamente qué se retiró.

## 8. Scripts históricos de raíz

NO mover ni eliminar en esta ronda:

- `probe_*.py`;
- `requirements-copilot.txt`;
- `result_codex/`;
- `context/.gitkeep`.

Clasificarlos como históricos/keep según R2.5.1.

## 9. Archivo `findstr`

R2.5.1 eliminó el archivo accidental `findstr`.

Mantener la eliminación.

Confirmar que:

- no hay referencias vigentes;
- no rompe tests;
- queda incluido en el checkpoint.

## 10. Import muerto

R2.5.1 eliminó `MODE_COLD` sin uso en `cache/session.py`.

Mantener el cambio.

No hacer más refactors de código.

## 11. Guardián pendiente de extraction cache

R2.5 dejó como `CURRENT_PHASE` que los módulos de formato/contrato de extraction cache no tienen guardián propio.

NO resolverlo en esta ronda administrativa.

Registrar que debe entrar al inicio de R2.6 o en el prompt de R2.6.

## 12. Tests

Como existe cambio previo de código (`cache/session.py`) y se hará commit checkpoint:

Ejecutar suite completa antes del commit:

`python -m unittest discover -s tests`

Criterio:

- 0 fallas;
- 0 errores.

Registrar total, skips y duración.

Si falla:

- NO commit;
- estado BLOCKED.

## 13. Revisión de Git antes del commit

Antes de crear el commit:

1. `git status --short`;
2. revisar todos los modificados/nuevos/eliminados;
3. confirmar que no hay:
   - outputs de medición;
   - `.tmp`;
   - caches accidentales;
   - archivos enormes no previstos;
   - secretos;
   - worktrees internos pendientes;
4. confirmar que `_cache_v53/` de mediciones no se está versionando;
5. revisar `git diff --stat`;
6. revisar `git diff --cached` solo después de staging.

No usar `git add .` sin revisar el listado.

## 14. Contenido del checkpoint

El commit debe incluir el trabajo coherente de V5.3 desde R0 hasta R2.5.1:

### Código

- R2.1 HydrationView;
- R2.2 write-skip/MAX_PATH;
- R2.2.1 writer refactor;
- R2.3 versions/fingerprints;
- R2.4 cache manifest/file state;
- R2.5 extraction cache;
- saneamiento R2.5.1.

### Tests

- tests V5.3 R2.1–R2.5;
- actualización de inventario de mantenibilidad;
- ajustes relacionados.

### Documentación

- resultados V5.3 R0 → R2.5.1;
- `V5_2_GIT_CLOSURE_RESULT.md` si sigue sin versionar;
- prompts V5.3 R0 → R2.5.1;
- actualización de continuidad;
- `PROJECT_STATE.json`.

### Eliminaciones

- `findstr`.

No incluir:

- salidas temporales;
- caches generadas;
- `.claude/`;
- `__pycache__/`;
- artefactos de medición.

## 15. Mensaje de commit

Usar un mensaje claro y único:

`feat(v5.3): checkpoint incremental cache foundation`

Si el estilo real del repositorio exige otro prefijo equivalente, justificarlo, pero no dividir en múltiples commits salvo que exista una razón objetiva.

## 16. Tag y push

NO crear tag.

NO ejecutar push.

Después del commit:

- mostrar hash;
- mostrar rama;
- confirmar `git status`;
- confirmar que el commit contiene los cambios previstos;
- detenerse.

El usuario decidirá más adelante cuándo publicar.

## 17. Estado esperado tras commit

Ideal:

- rama `main`;
- un nuevo commit local sobre `6c32c4c`;
- working tree limpio, salvo archivos explícitamente ignorados;
- sin worktrees residuales eliminables;
- continuidad actualizada;
- V5.3 todavía abierta;
- ningún tag nuevo.

Si quedan archivos no versionados legítimos, documentarlos y explicar por qué.

## 18. Seguridad Git

Prohibido:

- `git reset --hard`;
- `git clean -fd`;
- `git branch -D`;
- `git push`;
- `git push --force`;
- rebase;
- modificar commits existentes;
- borrar worktrees con cambios;
- borrar ramas no integradas.

## 19. Entregable

Crear:

`docs/V5/V5_3_R2_5_2_CONTINUITY_GIT_CHECKPOINT.md`

Debe incluir:

1. Objetivo.
2. Autorización aplicada.
3. PROJECT_STATE actualizado.
4. Continuidad/roadmap actualizado.
5. Worktrees detectados.
6. Validación de cada worktree.
7. Worktrees retirados/no retirados.
8. Ramas locales retiradas/no retiradas.
9. Archivos históricos preservados.
10. Suite completa.
11. Estado Git pre-commit.
12. Contenido del checkpoint.
13. Commit creado.
14. Hash del commit.
15. Estado Git post-commit.
16. Confirmación de no tag/no push.
17. Riesgos/deuda pendiente.
18. Recomendación para R2.6.
19. Estado final.

## 20. Estados finales permitidos

Si continuidad queda actualizada, suite verde, Git seguro y checkpoint creado:

`V5_3_R2_5_2_CHECKPOINT_CREATED`

Si hay worktree/branch con trabajo exclusivo o una decisión humana necesaria:

`V5_3_R2_5_2_NEEDS_HUMAN_DECISION`

Si tests fallan, el estado es incoherente o el commit no puede hacerse de forma segura:

`V5_3_R2_5_2_BLOCKED`

No usar otro estado.

## 21. Restricciones finales

No:

- iniciar R2.6;
- cambiar funcionalidad;
- corregir deuda ajena;
- crear tag;
- push;
- ejecutar IA.

Detenerse para revisión humana después del commit local.
