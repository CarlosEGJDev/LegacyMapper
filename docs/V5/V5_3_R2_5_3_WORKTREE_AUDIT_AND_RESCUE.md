# V5.3 R2.5.3 — Auditoría y rescate de worktrees residuales

Estado final: **V5_3_R2_5_3_NEEDS_HUMAN_DECISION** (auditoría completa: no hay nada que rescatar; el retiro no se ejecutó, ver §13)

## 1. Objetivo

Clasificar todos los cambios locales de los dos worktrees de R2.5.2 y retirarlos solo si era seguro.

## 2. Worktrees detectados

| | Ruta | Rama | HEAD |
|---|---|---|---|
| A | `.claude/worktrees/agent-a00511fc63aa090e0` | `worktree-agent-a00511fc63aa090e0` | `e9e3d60` |
| B | `.claude/worktrees/agent-a0c75b43cbf073bbc` | `worktree-agent-a0c75b43cbf073bbc` | `effea07` |

## 3. Estado Git de cada uno

Ambos: HEAD ancestro de `main`, 0 commits exclusivos (`main..rama` = 0).
- **A:** 286 modificados (19 con cambio real tras ignorar EOL) + 31 sin seguimiento (incl. `findstr`), 0 eliminados.
- **B:** 438 modificados (EOL casi todos) + 2 sin seguimiento, 0 eliminados.

Método: cada archivo cambiado o sin seguimiento se comparó (EOL normalizado) con `main` actual y con las últimas 12 revisiones de primer padre de `main`. Solo lectura.

## 4. Tabla completa — Worktree A

Del total (366 archivos con cambio o sin seguimiento): **353 son idénticos a `main`** (incluye los 31 sin seguimiento, ya versionados en `main` desde `effea07`/`44e2a94`: `docs/V4_3/`, `prompts/V4_3/`, `tests/test_v4_3_*`, `tools/v4_3_*`, `probe_*.py`, `requirements-copilot.txt`, `README.md`, `ai_projection.py`, etc.) → `ALREADY_SUPERSEDED`. Los 13 restantes:

| Archivo | Tipo de cambio | Diferencia funcional | Equivalente en main | Clasificación | Acción |
|---|---|---|---|---|---|
| `cli/parser.py` | instantánea V4.3 | = `44e2a94`/`6c32c4c`; `main` añade 12 líneas (V5.3 R2.2) | sí (versión posterior) | ALREADY_SUPERSEDED | ninguna |
| `cli/pipeline_stages.py` | instantánea V4.3 | = `44e2a94`; `main` añade HydrationView, extraction cache (R2.1–R2.5) | sí | ALREADY_SUPERSEDED | ninguna |
| `cli/router.py` | instantánea | = `6c32c4c`; +1 línea en `main` | sí | ALREADY_SUPERSEDED | ninguna |
| `cli/run_summary_presenter.py` | instantánea | = `44e2a94`; +4 líneas en `main` | sí | ALREADY_SUPERSEDED | ninguna |
| `cli/output_manifest.py` | sin seguimiento (instantánea) | = `6c32c4c`; `main` excluye `_cache_v53/` (R2.4) | sí | ALREADY_SUPERSEDED | ninguna |
| `context/hydration.py` | sin seguimiento (instantánea) | = `6c32c4c`; `main` usa `HydrationView` (R2.1) | sí | ALREADY_SUPERSEDED | ninguna |
| `context/ai_projection.py` | sin seguimiento (instantánea) | = `effea07`; `main` = versión de `44e2a94` (+70 líneas) | sí | ALREADY_SUPERSEDED | ninguna |
| `utils/atomic_write.py` | solo EOL | = su HEAD `e9e3d60`; `main` añade `atomic_write_bytes` (R2.4) | sí | ALREADY_SUPERSEDED | ninguna |
| `tests/test_v4_1_r0_maintainability_inventory.py` | instantánea | = `44e2a94`; `main` con inventario V5.3 | sí | ALREADY_SUPERSEDED | ninguna |
| `tests/test_v4_2_r3_deterministic_technical_documentation.py` | instantánea | = `44e2a94`; +5 líneas en `main` | sí | ALREADY_SUPERSEDED | ninguna |
| `tests/test_v4_r12_…contract.py`, `tests/test_v4_r14_manuals_and_final_baseline.py` | solo EOL | = su HEAD | sí | ALREADY_SUPERSEDED | ninguna |
| `output/v3_r9/READINESS_TRACEABILITY.json` | 3 hashes sha256 distintos | artefacto regenerado por una corrida de tests en el worktree; `main` conserva la versión versionada (`5f6af62`) | sí | DISCARD_SAFE | ninguna |
| `findstr` (sin seguimiento, 0 bytes) | artefacto accidental | vacío; ya eliminado de `main` en R2.5.1 | — | DISCARD_SAFE | ninguna |

Los otros ~270 «modificados» de A son solo EOL (cero diferencia funcional).

## 5. Análisis detallado de `ai_projection.py`

Cambio real en B (+56/−14 respecto de su HEAD `effea07`):
1. **Comportamiento:** el del presupuesto/selección del paquete `AI_HYDRATED_PROJECTION` de V4.3 (versión posterior del mismo archivo).
2. **Tipo:** feature/ajuste de V4.3, no V5.3.
3. **¿Ya en `main`?** Sí, **byte a byte** (EOL normalizado): la copia de B es idéntica a `main` (0 líneas de diferencia) y a `44e2a94` («Terminada la versión 4_3»), que fue el commit que la incorporó (`git log effea07..main -- ai_projection.py` = `44e2a94`). El diff vs HEAD y el diff `effea07→main` son idénticos (+56/−14).
4. **Tests:** sí, `tests/test_v4_3_*` (en `main`).
5. **Rompe contratos:** no; es la versión vigente.
6. **Pertenece a V5.3:** no (V4.3).
7. **Rescate:** ninguno; no hay nada que aplicar. **ALREADY_SUPERSEDED.**

En A, `ai_projection.py` es la versión anterior (`effea07`), sin seguimiento; también supersedida.

## 6. Archivos sin seguimiento

- **A (31):** `README.md`, `docs/V4_3/`, `prompts/V4_3/`, `probe_*.py` ×5, `requirements-copilot.txt`, módulos V4.3 (`output_manifest`, `ai_projection`, `consumer_projection`, `hydration`, `human_documentation_scaling`, `human_flow_documentation`, `_run_evidence_io`), 11 `tests/test_v4_3_*`, 3 `tools/v4_3_*`, `findstr`. Todos existen en `main` (idénticos o versión previa) salvo `findstr` (basura, 0 bytes). Código no integrado: ninguno.
- **B (2):** `docs/V4_3/V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md` y `tests/test_v4_3_r3a_r1_selection_packing_quality_correction.py`: ambos idénticos a `main` (documento útil/test ya versionados).
- Sin cachés, logs, temporales ni outputs rescatables. Secretos: ninguno nuevo (todo es contenido ya versionado).

## 7. Clasificación por archivo

Resumen: 353 + 434 (idénticos a `main`) y 18 instantáneas anteriores → `ALREADY_SUPERSEDED`; 2 → `DISCARD_SAFE`; 0 → `RESCUE`; 0 → `HISTORICAL_EXPERIMENT`; 0 → `NEEDS_HUMAN_DECISION` por contenido. B: sus 6 archivos distintos de `main` (`PROJECT_STATE.json`, `output_manifest.py`, `hydration.py`, `atomic_write.py`, tests r12/r14) son instantáneas de `effea07`/`e9e3d60` o solo EOL → `ALREADY_SUPERSEDED`.

## 8. Elementos RESCUE

Ninguno.

## 9. Elementos DISCARD_SAFE

`output/v3_r9/READINESS_TRACEABILITY.json` (A, artefacto regenerado) y `findstr` (A, vacío).

## 10. Elementos ALREADY_SUPERSEDED

Todo lo demás de A y B (§4–§7); reemplazados por `main` (`44e2a94`, `6c32c4c`, `2cb317f`).

## 11. Elementos HISTORICAL_EXPERIMENT

Ninguno.

## 12. Elementos NEEDS_HUMAN_DECISION

Solo el **procedimiento de retiro** (§13): por contenido no hay dudas.

## 13. Worktrees eliminados / no eliminados

**No eliminados.** Los dos cumplen la condición de §13 del prompt (todo supersedido/descartable, sin RESCUE, sin untracked valiosos), pero el intento de `git worktree remove <ruta>` (sin `--force`) fue **denegado por el clasificador de permisos del entorno** y no se reintentó por otra vía. Además, Git rechaza por defecto retirar worktrees con archivos modificados/sin seguimiento, y `--force` está prohibido por el prompt. Hace falta decisión/acción humana (ver §19).

## 14. Ramas eliminadas / no eliminadas

Ninguna eliminada (`git branch -d` no se ejecutó; sin `-D`). Ambas ramas están integradas en `main`.

## 15. Estado de `main`

Sin cambios de funcionalidad ni commits: HEAD `2cb317f`, working tree sin otras diferencias que los documentos nuevos no versionados.

## 16. Estado del checkpoint `2cb317f`

Intacto (`2cb317fe5ae3dd2cbad1f865b1faee4a50a99569`): sin amend, rebase ni reescritura.

## 17. Documento R2.5.2 pendiente

`docs/V5/V5_3_R2_5_2_CONTINUITY_GIT_CHECKPOINT.md` **sigue sin versionar**, igual que los prompts `prompts/V5/V5_3_R2_5_3_…` y este documento; deberán entrar en un futuro commit administrativo o funcional. No se hizo commit.

## 18. Riesgos

Ninguno de contenido: los worktrees no contienen trabajo único. Riesgo operativo menor: 32 MB residuales en `.claude/worktrees/` y dos ramas locales que seguirán apareciendo en `git branch`. Un retiro forzado equivocado (p. ej. `-D`) no sería destructivo respecto del trabajo (todo está en `main`), pero se evitó por contrato.

## 19. Recomendación concreta

Dado que no hay nada que rescatar, el usuario puede ejecutar él mismo (o autorizar explícitamente a un agente a ejecutar):

```text
git worktree remove --force .claude/worktrees/agent-a00511fc63aa090e0
git worktree remove --force .claude/worktrees/agent-a0c75b43cbf073bbc
git branch -d worktree-agent-a00511fc63aa090e0 worktree-agent-a0c75b43cbf073bbc
git worktree prune
```

(`--force` es necesario solo porque los worktrees están sucios con copias supersedidas; `-d` funcionará porque las ramas están integradas.) Después, R2.6 puede iniciarse con el guardián de la extraction cache.

## 20. Estado final

Auditoría completa y sin hallazgos de rescate; retiro pendiente de autorización humana.

**V5_3_R2_5_3_NEEDS_HUMAN_DECISION**
