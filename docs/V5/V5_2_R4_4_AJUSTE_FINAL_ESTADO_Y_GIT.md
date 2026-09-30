# V5.2 R4.4 — Ajuste final de estado y preparación Git

## 1. Inconsistencia corregida

`PROJECT_STATE.json` → `known_risks.r6_intermittent_test.status` decía `NON_REPRODUCIBLE_AS_OF_V4.2_FORMAL_CLOSURE`, aunque `docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md` identificó la causa y aplicó una corrección (reintento acotado ante `PermissionError` transitorio de `os.replace` en `atomic_write_text`). Prevalece la evidencia posterior. No se inventó ninguna causa nueva: se cita la ya documentada.

## 2. Cambio exacto en `PROJECT_STATE.json`

Solo dentro de `known_risks.r6_intermittent_test` (no se tocó ningún otro riesgo ni clave):

| Clave | Antes | Después |
|---|---|---|
| `status` | `NON_REPRODUCIBLE_AS_OF_V4.2_FORMAL_CLOSURE` | `ROOT_CAUSE_IDENTIFIED_AND_FIXED` |
| `historical_status` | (no existía) | `NON_REPRODUCIBLE_AS_OF_V4.2_FORMAL_CLOSURE` (se conserva el hecho histórico) |
| `note` | «No recurrió… V5 debe tratar cualquier recurrencia como disparador» | Texto en inglés (idioma de la clave) que conserva lo histórico, cita el informe de causa raíz, la corrección `_replace_with_retry`, la cobertura de tests añadida en V5.2 R4.2 y mantiene la regla de investigar cualquier recurrencia |
| `root_cause_report_path` | — | `docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md` |
| `fix` | — | `bounded PermissionError retry around os.replace (_replace_with_retry)` |
| `test_coverage_added_in` | — | `V5.2-R4.2` |

`test` y `observed_in` sin cambios.

## 3. Validación JSON

`json.load` sobre `PROJECT_STATE.json`: válido.

## 4. Tests dirigidos ejecutados

Los que consumen o validan `PROJECT_STATE.json`: `test_v4_r11_human_readable_document_projection`, `test_v4_r12_plugin_facing_machine_readable_output_contract`, `test_v4_r13_regression_and_security`, `test_v4_r14_manuals_and_final_baseline`, `test_v4_1_r1_regression_and_json_renderer`, `test_v4_1_r4_readiness_characterization`, `test_v4_3_r7_internal_acceptance`.

## 5. Resultado

**292 pruebas, OK** (38 s). No se modificó código ni tests en esta ronda, por lo que **no se repitió la suite completa**: la vigente sigue siendo la de R4.3 (2.449 pruebas, 0 fallas, 0 errores, 132 skips).

## 6. Estado Git (solo consultas)

- Rama: `main`. Remote: `origin` (`https://github.com/CarlosEGJDev/LegacyMapper.git`). `HEAD` de partida: `ee472f7` (igual a `origin/main` al comprobarse en R4.3).
- Tag `v5.2`: no existe (`git tag -l v5.2` vacío).
- Diff de seguimiento: 15 archivos modificados/borrados (757 inserciones, 332 borrados). Sin seguimiento: 110 archivos (con `-uall`).
- Aviso de Git: `LF will be replaced by CRLF` en varios archivos (`PROJECT_STATE.json`, continuidad, `atomic_write.py`, tests). No es un error; puede generar ruido en diffs.

## 7. Archivos que entrarían al commit (`git add -A`)

**Modificados (14) y borrado (1):** `CLAUDE.md`; `PROJECT_STATE.json`; 4 documentos de `docs/continuity/` (working rules, lecciones, historia, roadmap); `legacy_documenter/cli/pipeline_stages.py`, `run_summary_presenter.py`, `legacy_documenter/utils/atomic_write.py`; 6 tests históricos (`test_v4_1_r0_maintainability_inventory`, `test_v4_2_r3_deterministic_technical_documentation`, `test_v4_r12…`, `test_v4_r13…`, `test_v4_r14…`); borrado `docs/V5_0/V5_0_R0_EMPIRICAL_BASELINE_AND_ARCHITECTURE_PREP_PROMPT.md` (se movió a `prompts/V5_0/`, idéntico).

**Nuevos, agrupados:** `docs/V5/` (informes V5, incluidos R4, R4.1, R4.2, R4.3 y este), `prompts/V5_0/` (prompts V5, incluidos R4.1 a R4.4), `legacy_documenter/evidence/` (8), `legacy_documenter/documentation_v52/` (31, con defaults JSON), 8 tests `tests/test_v5_*`, 3 herramientas `tools/v5_*`.

## 8. Archivos dudosos o ajenos

Ninguno claramente ajeno al trabajo V5. Puntos a decidir por el usuario:

1. `CLAUDE.md`: añade reglas de creación de documentación; no es código V5 pero es cambio intencional del proyecto. Puede ir en el mismo commit o en uno separado.
2. `docs/continuity/*` y las 3 modificaciones de tests V4 son mantenimiento de continuidad del cierre V5.
3. `prompts/V5_0/V5_1_R2_1_Normalized_Evidence_Core_Saneamiento_e_Integración.md` tiene una tilde en el nombre (no es un problema de Git, solo un nombre no ASCII).
4. No aparecen `.zip`, logs, `output/` ni cachés en las rutas sin seguimiento; `__pycache__` y `.claude/worktrees/` están ignorados/excluidos.

## 9. Commit propuesto

`chore(v5.2): close documentation profiles phase`

## 10. Tag propuesto

`v5.2` (anotado). Rama esperada `main`; remote esperado `origin`.

## 11. Comandos preparados (NO ejecutados)

```bat
cd /d C:\dev\LegacyMapper
git add -A
git status
git commit -m "chore(v5.2): close documentation profiles phase"
git tag -a v5.2 -m "V5.2 Template-Driven Documentation & Output Profiles - closed"
git push origin main
git push origin v5.2
```

Tras el commit, registrar hash, tag, rama, remote y fecha (hoy `PENDING_GIT_APPROVAL`).

## 12. Confirmación Git

No se hizo commit, tag ni push, ni ninguna operación que cambie historial. Solo consultas de lectura.

## 13. V5.3

No fue iniciada.

Archivos modificados en esta ronda: `PROJECT_STATE.json` (solo lo indicado en §2) y este informe. Sin código, tests, roadmap, continuidad ni informes históricos tocados.

**V5_2_READY_FOR_GIT_APPROVAL**
