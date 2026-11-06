# LegacyMapper V5.3 — R2.5.4 Backup preventivo y limpieza final de worktrees

## 1. Objetivo

Cerrar de forma segura la limpieza de los worktrees residuales detectados en R2.5.2/R2.5.3.

Antes de eliminar nada, crear dos capas de respaldo:

1. una rama local de respaldo del estado consolidado de `main`;
2. un respaldo externo de los cambios no committeados de ambos worktrees.

Solo después de verificar ambos respaldos se autoriza retirar los worktrees con `--force`.

NO iniciar R2.6.

---

## 2. Autorización humana

El usuario autorizó explícitamente:

- crear una rama local de respaldo;
- crear respaldo externo de los cambios locales de los worktrees;
- eliminar ambos worktrees residuales después de verificar los respaldos;
- usar `git worktree remove --force` únicamente para esos dos worktrees ya auditados;
- eliminar sus ramas locales con `git branch -d`;
- ejecutar `git worktree prune`;
- crear un commit administrativo local final con la documentación pendiente de R2.5.2–R2.5.4, si todo queda limpio.

NO está autorizado:

- push;
- tag;
- `git branch -D`;
- reset destructivo;
- `git clean`;
- rebase;
- amend del checkpoint;
- iniciar R2.6.

---

## 3. Fuentes obligatorias

Leer antes de actuar:

- `docs/V5/V5_3_R2_5_2_CONTINUITY_GIT_CHECKPOINT.md`
- `docs/V5/V5_3_R2_5_3_WORKTREE_AUDIT_AND_RESCUE.md`
- `docs/V5/V5_3_R2_5_1_REPOSITORY_HYGIENE_AUDIT.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

Checkpoint vigente:

`2cb317fe5ae3dd2cbad1f865b1faee4a50a99569`

---

## 4. Precondiciones

Antes de crear respaldos:

1. confirmar rama actual:
   `main`;
2. confirmar HEAD:
   `2cb317f` o descendiente administrativo explícitamente esperado;
3. ejecutar:
   `git status --short`;
4. confirmar que no hay cambios funcionales nuevos inesperados;
5. confirmar los dos worktrees objetivo con:
   `git worktree list --porcelain`.

Si aparece cualquier worktree adicional relevante o cambios funcionales nuevos no explicados:

`V5_3_R2_5_4_BLOCKED`

---

## 5. Rama de respaldo

Crear una rama local:

`backup/v5.3-pre-worktree-cleanup`

Debe apuntar exactamente al HEAD actual de `main` antes de limpiar.

Usar:

`git branch backup/v5.3-pre-worktree-cleanup HEAD`

No cambiarse a esa rama.

Verificar:

`git rev-parse backup/v5.3-pre-worktree-cleanup`

debe coincidir con:

`git rev-parse HEAD`

Registrar ambos hashes.

Si la rama ya existe:

- verificar a qué commit apunta;
- NO sobrescribirla;
- si coincide con HEAD, reutilizar;
- si no coincide, detenerse con `NEEDS_HUMAN_DECISION`.

---

## 6. Respaldo externo de worktrees

Una rama NO conserva modificaciones sin commit.

Por eso, antes de borrar los worktrees, crear un respaldo externo fuera del repositorio principal.

Ruta recomendada:

`C:\dev\LegacyMapper_backups\v5_3_r2_5_4_worktrees\`

Si ya existe, crear una subcarpeta nueva o verificar que no se sobrescriba información previa.

Nunca guardar este backup dentro del repo LegacyMapper.

---

## 7. Worktrees objetivo

### A

Ruta:

`.claude/worktrees/agent-a00511fc63aa090e0`

Rama:

`worktree-agent-a00511fc63aa090e0`

### B

Ruta:

`.claude/worktrees/agent-a0c75b43cbf073bbc`

Rama:

`worktree-agent-a0c75b43cbf073bbc`

No operar sobre otros worktrees.

---

## 8. Backup del Worktree A

Dentro del worktree A:

### 8.1 Metadata

Guardar en el backup externo:

- HEAD;
- rama;
- `git status --short`;
- `git diff --stat`;
- `git diff --name-status`;
- `git ls-files --others --exclude-standard`.

### 8.2 Patch

Crear:

`worktree_A_tracked_changes.patch`

con:

`git diff --binary HEAD`

Debe contener todos los cambios tracked no committeados, incluidos binarios si los hubiera.

### 8.3 Untracked

Crear:

`worktree_A_untracked_files.txt`

con la lista exacta de archivos sin seguimiento.

Copiar físicamente los archivos untracked a:

`worktree_A_untracked/`

preservando estructura relativa.

No copiar:

- `.git`;
- caches ignoradas;
- `__pycache__`;
- otros archivos ignorados que no aparezcan en la lista untracked.

---

## 9. Backup del Worktree B

Repetir exactamente el mismo procedimiento:

- `worktree_B_metadata.txt`
- `worktree_B_tracked_changes.patch`
- `worktree_B_untracked_files.txt`
- `worktree_B_untracked/`

---

## 10. Verificación de respaldos

Antes de eliminar worktrees:

1. comprobar que ambos patches existen;
2. comprobar que los listados untracked existen;
3. comprobar que el número de untracked respaldados coincide con el listado;
4. calcular SHA-256 de:
   - cada `.patch`;
   - cada metadata/listado;
5. registrar tamaños;
6. confirmar que el directorio externo está FUERA del repo;
7. confirmar que la rama backup existe y apunta al HEAD esperado.

Si falla cualquier verificación:

NO eliminar worktrees.

Estado:

`V5_3_R2_5_4_BLOCKED`

---

## 11. Confirmación contra auditoría R2.5.3

Antes del `--force`, confirmar nuevamente:

- 0 `RESCUE`;
- 0 `NEEDS_HUMAN_DECISION` por contenido;
- commits de ambas ramas ya contenidos en `main`;
- 0 commits exclusivos;
- contenido clasificado únicamente como:
  - `ALREADY_SUPERSEDED`;
  - `DISCARD_SAFE`.

Si esto ya no se cumple:

NO limpiar.

---

## 12. Limpieza autorizada

Solo después de completar §§5–11.

Ejecutar:

```text
git worktree remove --force .claude/worktrees/agent-a00511fc63aa090e0
git worktree remove --force .claude/worktrees/agent-a0c75b43cbf073bbc
```

El uso de `--force` está autorizado exclusivamente para estos dos worktrees y únicamente después de verificar los backups.

No usar `--force` en ningún otro worktree.

---

## 13. Eliminación segura de ramas locales

Después de retirar los worktrees:

```text
git branch -d worktree-agent-a00511fc63aa090e0
git branch -d worktree-agent-a0c75b43cbf073bbc
```

NO usar:

`git branch -D`

Si `-d` falla:

- no forzar;
- documentar;
- `NEEDS_HUMAN_DECISION`.

---

## 14. Prune

Ejecutar:

`git worktree prune`

Luego verificar:

`git worktree list --porcelain`

Debe quedar únicamente el/los worktrees legítimos actualmente esperados.

---

## 15. Verificación post-limpieza

Confirmar:

- `main` intacta;
- HEAD no cambió por la limpieza;
- rama backup sigue existiendo;
- worktrees A/B ya no aparecen;
- ramas A/B eliminadas si `-d` fue exitoso;
- backup externo intacto;
- no se modificó runtime;
- no se perdió ningún archivo del repo principal.

---

## 16. Documentos pendientes

Antes de esta ronda están pendientes de versionar:

- `docs/V5/V5_3_R2_5_2_CONTINUITY_GIT_CHECKPOINT.md`
- `prompts/V5/V5_3_R2_5_3_WORKTREE_AUDIT_AND_RESCUE.md`
- `docs/V5/V5_3_R2_5_3_WORKTREE_AUDIT_AND_RESCUE.md`

También se añadirán:

- `prompts/V5/V5_3_R2_5_4_BACKUP_AND_WORKTREE_CLEANUP.md`
- `docs/V5/V5_3_R2_5_4_BACKUP_AND_WORKTREE_CLEANUP.md`

No versionar el backup externo.

---

## 17. Tests

La limpieza no modifica runtime.

Por tanto:

- no es obligatorio repetir la suite completa si `git diff` confirma que no se cambió código;
- ejecutar al menos:
  - validación de `PROJECT_STATE.json`;
  - `git status`;
  - `git diff --check`.

Si aparece cualquier cambio de runtime inesperado:

- NO commit;
- ejecutar suite completa;
- investigar.

---

## 18. Commit administrativo final

Si:

- backup correcto;
- worktrees retirados;
- ramas eliminadas con `-d`;
- main intacta;
- documentos pendientes completos;
- no hay cambios funcionales nuevos;

crear un commit local administrativo.

Mensaje:

`chore(v5.3): finalize pre-r2.6 repository cleanup`

Debe incluir solamente:

- documentos/prompts pendientes R2.5.2–R2.5.4;
- cualquier actualización documental estrictamente necesaria generada por esta ronda.

No incluir backup externo.

No incluir `.claude/`.

No incluir caches.

---

## 19. Rama de respaldo

La rama:

`backup/v5.3-pre-worktree-cleanup`

NO debe borrarse en esta ronda.

Debe quedar disponible como punto de retorno.

No hacer push de ella.

---

## 20. Recuperación si algo sale mal

Documentar comandos de recuperación.

### Volver al checkpoint consolidado

La rama backup apunta al estado previo:

`backup/v5.3-pre-worktree-cleanup`

No ejecutar ningún reset automáticamente.

### Recuperar cambios tracked de un worktree

Usar el patch externo:

`git apply <worktree_X_tracked_changes.patch>`

solo en una rama/worktree de recuperación, nunca automáticamente sobre `main`.

### Recuperar untracked

Copiar desde:

`worktree_X_untracked/`

a una rama/worktree de recuperación.

La existencia de estos respaldos debe verificarse antes de cerrar la ronda.

---

## 21. Git prohibido

No:

- push;
- tag;
- force push;
- branch `-D`;
- reset `--hard`;
- clean;
- rebase;
- amend;
- borrar la rama backup;
- borrar el backup externo.

---

## 22. Entregable

Crear:

`docs/V5/V5_3_R2_5_4_BACKUP_AND_WORKTREE_CLEANUP.md`

Debe incluir:

1. Objetivo.
2. Estado inicial.
3. Rama backup creada.
4. Hash de `main`.
5. Hash de rama backup.
6. Ruta del backup externo.
7. Backup Worktree A.
8. Backup Worktree B.
9. SHA-256 y tamaños de backups.
10. Verificación pre-limpieza.
11. Worktrees eliminados.
12. Ramas eliminadas.
13. Resultado de prune.
14. Estado de main post-limpieza.
15. Rama backup preservada.
16. Documentos añadidos.
17. Tests/validaciones.
18. Commit administrativo.
19. Hash del commit.
20. Confirmación no push/no tag.
21. Procedimiento de recuperación.
22. Riesgos pendientes.
23. Recomendación para R2.6.
24. Estado final.

---

## 23. Estados finales permitidos

Si backup + limpieza + commit administrativo se completan:

`V5_3_R2_5_4_CLEANUP_COMPLETE`

Si los backups están hechos pero alguna rama/worktree no puede retirarse de forma segura:

`V5_3_R2_5_4_NEEDS_HUMAN_DECISION`

Si falla el backup, cambia main inesperadamente o hay riesgo de pérdida:

`V5_3_R2_5_4_BLOCKED`

---

## 24. Criterio de cierre

La ronda queda lista si:

- existe la rama local `backup/v5.3-pre-worktree-cleanup`;
- apunta al estado pre-limpieza correcto;
- ambos worktrees tienen backup externo verificable;
- no queda trabajo único sin respaldo;
- ambos worktrees residuales fueron retirados;
- sus ramas fueron eliminadas con `-d`;
- `main` permanece correcto;
- los documentos pendientes quedaron versionados;
- existe un commit administrativo local;
- no hubo push ni tag;
- R2.6 puede comenzar desde un repositorio limpio.

Detenerse para revisión humana.
