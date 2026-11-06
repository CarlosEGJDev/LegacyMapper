# LegacyMapper V5.3 — R2.5.3 Auditoría y rescate de worktrees residuales

## 1. Objetivo

Resolver de forma segura los dos worktrees residuales detectados en R2.5.2.

La ronda debe determinar, para cada cambio local encontrado, si:

- ya está supersedido por `main`;
- es trabajo experimental descartable;
- contiene valor que debe rescatarse;
- requiere decisión humana.

NO iniciar R2.6.

## 2. Fuentes obligatorias

Leer antes de actuar:

- `docs/V5/V5_3_R2_5_1_REPOSITORY_HYGIENE_AUDIT.md`
- `docs/V5/V5_3_R2_5_2_CONTINUITY_GIT_CHECKPOINT.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

Consultar también:

- `git worktree list --porcelain`
- estado Git de cada worktree
- historial de `main`
- diff de cada worktree contra su HEAD
- diff de cada worktree contra `main`

## 3. Worktrees objetivo

Según R2.5.2:

### A

`.claude/worktrees/agent-a00511fc63aa090e0`

Rama:

`worktree-agent-a00511fc63aa090e0`

HEAD:

`e9e3d60`

Estado previo:

- commit integrado en `main`;
- 0 commits exclusivos;
- 19 archivos con cambios reales tras ignorar ruido de EOL;
- además archivos sin seguimiento.

### B

`.claude/worktrees/agent-a0c75b43cbf073bbc`

Rama:

`worktree-agent-a0c75b43cbf073bbc`

HEAD:

`effea07`

Estado previo:

- commit integrado en `main`;
- 0 commits exclusivos;
- cambio real principal en:
  `legacy_documenter/context/ai_projection.py`
- además archivos sin seguimiento.

## 4. Regla principal

NO borrar ningún worktree hasta clasificar completamente sus cambios.

Cada cambio debe terminar en una categoría:

- `ALREADY_SUPERSEDED`
- `DISCARD_SAFE`
- `RESCUE`
- `HISTORICAL_EXPERIMENT`
- `NEEDS_HUMAN_DECISION`

Si existe duda razonable:

`NEEDS_HUMAN_DECISION`

## 5. Auditoría por worktree

Para cada worktree:

1. ejecutar `git status --short`;
2. separar:
   - modificados;
   - eliminados;
   - nuevos;
   - sin seguimiento;
3. obtener diff contra su HEAD;
4. obtener diff contra `main`;
5. identificar cambios solo de:
   - EOL;
   - whitespace;
   - formatting;
6. excluir ese ruido del análisis funcional;
7. revisar cada cambio real;
8. buscar si la misma lógica ya existe en `main`;
9. buscar referencias en:
   - docs;
   - tests;
   - commits posteriores;
10. clasificar.

## 6. Worktree A — análisis obligatorio

Para los ~19 archivos con cambios reales:

Crear una tabla:

| Archivo | Tipo de cambio | Diferencia funcional | Existe equivalente en main | Clasificación | Acción recomendada |

Revisar especialmente:

- cambios de runtime;
- tests;
- documentación;
- prompts;
- configuraciones;
- scripts de diagnóstico;
- artefactos temporales.

No asumir que un diff grande implica trabajo valioso.

## 7. Worktree B — `ai_projection.py`

Analizar con detalle:

`legacy_documenter/context/ai_projection.py`

Comparar:

- versión del worktree;
- versión de su HEAD;
- versión actual de `main`.

Responder:

1. ¿qué comportamiento cambia?
2. ¿es bugfix, experimento, refactor o feature?
3. ¿ya está implementado de otra forma en `main`?
4. ¿tiene tests?
5. ¿rompe contratos actuales?
6. ¿pertenece a V5.3?
7. ¿debería rescatarse ahora o diferirse?

No incorporar automáticamente el cambio.

## 8. Archivos sin seguimiento

Para cada archivo untracked:

Clasificar:

- temporal;
- medición;
- script de experimento;
- documento útil;
- fixture;
- código no integrado;
- basura accidental.

No rescatar:

- caches;
- logs;
- temporales;
- outputs;
- copias redundantes;
- archivos generados.

## 9. RESCUE

Si algún cambio merece rescate:

NO modificar `main` todavía.

Crear una propuesta concreta:

- archivo;
- fragmento/lógica a rescatar;
- motivo;
- riesgo;
- tests necesarios;
- ronda apropiada para incorporarlo.

Si el rescate es trivial, aislado y claramente correcto, aun así NO aplicarlo sin autorización humana dentro de esta ronda.

## 10. DISCARD_SAFE

Solo clasificar como `DISCARD_SAFE` si:

- no hay commits exclusivos;
- el cambio está supersedido o no aporta valor;
- no hay referencias;
- no contiene trabajo único;
- no afecta continuidad;
- no contiene secretos o datos que deban conservarse.

Documentar evidencia.

## 11. ALREADY_SUPERSEDED

Usar cuando:

- el cambio local tiene equivalente funcional en `main`;
- o el código actual de `main` evolucionó más allá de ese trabajo.

Indicar qué archivo/commit actual lo reemplaza.

## 12. HISTORICAL_EXPERIMENT

Usar para:

- pruebas exploratorias;
- prototipos;
- spikes;
- scripts de diagnóstico;
- cambios abandonados pero comprensibles históricamente.

No mover ni archivar en esta ronda salvo necesidad clara.

## 13. Eliminación de worktrees

Solo se permite eliminar un worktree si:

- TODOS sus cambios están en:
  - `DISCARD_SAFE`,
  - `ALREADY_SUPERSEDED`,
  - `HISTORICAL_EXPERIMENT`;
- no existe ningún `RESCUE`;
- no existe ningún `NEEDS_HUMAN_DECISION`;
- no hay archivos sin seguimiento valiosos.

Si cumple:

1. `git worktree remove <path>`;
2. `git branch -d <branch>`;
3. `git worktree prune`.

NO usar:

- `git worktree remove --force`;
- `git branch -D`.

## 14. Si hay RESCUE o duda

Si un worktree contiene algo de valor:

- NO eliminar;
- no tocar su rama;
- no modificar main;
- documentar qué debe rescatarse;
- estado final:
  `V5_3_R2_5_3_NEEDS_HUMAN_DECISION`.

## 15. Estado de `main`

No modificar funcionalidad de `main`.

Solo se permite:

- crear el informe;
- si ambos worktrees son eliminables, registrar su limpieza.

No hacer commit en esta ronda salvo que el único cambio sea el informe y el usuario lo haya autorizado expresamente. Como no hay autorización adicional para un nuevo commit:

**NO commit.**

## 16. Checkpoint existente

Preservar:

`2cb317fe5ae3dd2cbad1f865b1faee4a50a99569`

No reescribirlo.

No amend.

No rebase.

## 17. Documento R2.5.2 pendiente

El archivo:

`docs/V5/V5_3_R2_5_2_CONTINUITY_GIT_CHECKPOINT.md`

sigue sin versionar.

NO hacer commit todavía.

Solo registrar que sigue pendiente y que deberá incluirse en un futuro commit administrativo o funcional.

## 18. Tests

Si NO se modifica runtime/main:

- no hace falta suite completa;
- sí ejecutar cualquier test puntual necesario para evaluar un posible RESCUE.

Si accidentalmente se modifica runtime:

- revertir el cambio;
- esta ronda no autoriza cambios funcionales.

## 19. Git

Permitido:

- `git status`
- `git diff`
- `git log`
- `git show`
- `git merge-base`
- `git branch --contains`
- `git worktree list`
- `git worktree remove` solo si cumple §13
- `git branch -d` solo si cumple §13
- `git worktree prune`

Prohibido:

- commit
- push
- tag
- reset
- clean
- rebase
- branch -D
- worktree remove --force

## 20. Entregable

Crear:

`docs/V5/V5_3_R2_5_3_WORKTREE_AUDIT_AND_RESCUE.md`

Debe incluir:

1. Objetivo.
2. Worktrees detectados.
3. Estado Git de cada uno.
4. Tabla completa Worktree A.
5. Análisis detallado de `ai_projection.py`.
6. Archivos untracked.
7. Clasificación por archivo.
8. Elementos `RESCUE`.
9. Elementos `DISCARD_SAFE`.
10. Elementos `ALREADY_SUPERSEDED`.
11. Elementos `HISTORICAL_EXPERIMENT`.
12. Elementos `NEEDS_HUMAN_DECISION`.
13. Worktrees eliminados/no eliminados.
14. Ramas eliminadas/no eliminadas.
15. Estado de `main`.
16. Estado del checkpoint `2cb317f`.
17. Documento R2.5.2 pendiente.
18. Riesgos.
19. Recomendación concreta.
20. Estado final.

## 21. Estados finales permitidos

Si ambos worktrees se pueden eliminar con seguridad y se eliminan:

`V5_3_R2_5_3_WORKTREES_CLEANED`

Si hay cualquier trabajo potencialmente valioso o ambiguo:

`V5_3_R2_5_3_NEEDS_HUMAN_DECISION`

Si la auditoría no puede completarse con seguridad:

`V5_3_R2_5_3_BLOCKED`

No usar otro estado.

## 22. Restricciones finales

No:

- iniciar R2.6;
- modificar funcionalidad;
- rescatar código automáticamente;
- commit;
- push;
- tag;
- borrar con force;
- descartar trabajo ambiguo;
- ejecutar IA.

Detenerse para revisión humana.
