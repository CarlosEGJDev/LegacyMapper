# Post-V5 — Resultado de la consolidación documental

Ronda solo de documentación/estado. Sin cambios de producto, tests, esquemas ni contratos; sin commit, push ni tag; V6 no iniciada; H1–H5 **no** implementados.

## 1. Archivos inspeccionados
`AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.json`, `README.md`, `docs/PROJECT_RECOVERY.md`, los cinco documentos de `docs/continuity/`, `docs/V5/V5_OPERATIONS_GUIDE.md`, `V5_FINAL_CLOSURE.md/.json`, `V5_FINAL_DEBT_LEDGER.json`, `V5_FINAL_BASELINE.json`; notas clean-room (`C:\PruebasLegacyMapper\V5_USER_ACCEPTANCE\notes\`, producidas en la ronda anterior de esta misma sesión).

## 2. Archivos actualizados
`PROJECT_STATE.json`; `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`; `LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`; `LEGACYMAPPER_LESSONS_LEARNED.md` (§37); `CLAUDE_CODE_CLI_BEST_PRACTICES.md` (§40); `ASSISTANT_WORKING_RULES_AND_PREFERENCES.md` (§28); `docs/V5/V5_OPERATIONS_GUIDE.md` (§10); `README.md`, `docs/PROJECT_RECOVERY.md`, `CLAUDE.md` (solo punteros).

## 3. Archivos creados
`docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md`; `docs/POST_V5/LEGACYMAPPER_PRODUCT_PRINCIPLES.md` (aporta: principios estables independientes de la versión; no existía equivalente canónico); este informe.

## 4. Roadmap canónico seleccionado
`docs/continuity/LEGACYMAPPER_V5_ROADMAP.md` (`active_roadmap_path`) para V5 + puntero a `docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md` para la iniciativa activa. `LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md` es el documento de continuidad a largo plazo (§38 nueva).

## 5. Duplicados / documentos obsoletos
No se encontraron copias `(1)` ni duplicados divergentes bajo el repositorio (búsqueda en el árbol versionado); no hay ambigüedad de propiedad canónica. Los dos documentos de roadmap/historia acumulaban cabeceras históricas apiladas: se mantuvieron, con una cabecera vigente nueva por encima y las anteriores rotuladas «Histórico».

## 6. Estado final de V5 registrado
V5.0–V5.9 CLOSED, Closure R1 aprobada, sin R2, R3 completada; commit de cierre `e831a2f84d2749b4452e06860521b3171093c7b9`; tag `v5` anotado publicado (→ ese commit); sincronización post-tag `90efa975e44abbd0314bd0793fe3f9d37ff13432` (no es destino del tag); analyzer v3 `f05b2de4…`; IST 15138 → 47523 archivos / 2828066791 bytes, 0/0/0; piloto Python circular; tests 3100/970, 132 skips; deuda 0/14/15/5. Valores históricos no alterados.

## 7. Hechos del clean-room incorporados
Ruta y método (`git archive v5`, `.venv` propio, Python 3.14.7), sin imports desde el repo de desarrollo, ejecución desde fuente con `python main.py`, sin `pyproject.toml`, sin dependencias de terceros, sin CLI de consumers; `--long-paths`; `full` sobre repo inexistente → SUCCESS vacío; Fake provider genérico → `INVALID_OUTPUT` (guard esperado); ruta PowerShell `..\.venv\Scripts\python.exe`; **PowerShell no validado** (bloqueado por directiva de grupo; CLI validada en Git Bash) — así consta en PROJECT_STATE, guía operativa y lecciones.

## 8. Roadmap H1–H5
Registrado en el roadmap post-V5 y resumido en el roadmap V5 y en la historia §38.7; primera ronda recomendada H1-R1. Capacidad AI-only descrita como **capacidad futura** (sin nombre de comando fijado, `AI_ONLY_INPUT_INVALID` conceptual).

## 9. Lecciones añadidas
`LEGACYMAPPER_LESSONS_LEARNED.md` §37: regla permanente de ejecución de hitos (§37.1: 1 prompt; ≤3 rondas; hasta 5 excepcional; re-diagnosticar), producto, arquitectura, IA, proceso, Windows/runtime, UX clean-room, cada ítem clasificado (lección / limitación aceptada / defecto candidato / capacidad futura).

## 10. Buenas prácticas añadidas
`CLAUDE_CODE_CLI_BEST_PRACTICES.md` §40 y `ASSISTANT_WORKING_RULES_AND_PREFERENCES.md` §28.

## 11. Contradicciones obsoletas que permanecen (intencionalmente históricas)
`V5_0_READY_TO_START` / `Vx_READY_TO_START` y `IN_PROGRESS` en instantáneas rotuladas «Histórico» de los dos documentos de continuidad; `TAG_NOT_CREATED_PENDING_HUMAN_DECISION` y `V5_CLOSURE_R1_READY_FOR_HUMAN_REVIEW` en recibos históricos (`V5_FINAL_CLOSURE.md` §20 lo narra como estado al cierre, `V5_CLOSURE_R1_RESULT.json`, auditoría R1, prompts de cierre, `V5_9_R3…`, `prompts/V5_0/…`); la ruta histórica `C:\inetpub\wwwroot\2010\IST\Operacional` en documentos V4.x/V5.0/V5.1/V5.2 (en la historia se rotuló explícitamente como histórica; la ruta oficial del baseline V5 es `C:\Users\cgalianj\source\IST_40\Operacional`). Los textos de orientación vigente (README, RECOVERY, CLAUDE, cabeceras de los roadmaps, PROJECT_STATE) no contienen estados obsoletos.

## 12. Ambigüedades / bloqueos
**Hallazgo (no resuelto aquí, fuera del alcance «sin cambios de código/tests»):** cinco tests históricos que parsean `PROJECT_STATE.json` fallan con `latest_approved_round = "V5-Closure-R1"`, valor que ya estaba en el commit de cierre `e831a2f` (la suite completa de Closure R3 se ejecutó **antes** de esa edición de estado):
`test_v4_r13…test_project_state_round_is_at_least_r12`, `test_v4_r14…test_project_state_at_least_r13_approved`, `test_v4_r14…DeterminismTests.test_baseline_matches_on_disk_artifact`, `test_v4_r12…test_project_state_records_r11_approved`, `test_v4_1_r1…RoundOrdinalParsingFixTests.test_project_state_round_ordinal_tests_pass` (este último agrega los anteriores). Reproducidos también con el árbol limpio de `HEAD` (git stash), es decir, no los causa esta ronda. Causa: sus regex aceptan `V[45](.n)?-R<N>` y no `V5-Closure-R1`. Por eso en esta ronda `latest_completed_round`/`latest_approved_round` **no** se modificaron (la nueva ronda se registra en `post_v5_latest_round`). Corrección propuesta (requiere autorización, es cambio de tests): generalizar esos parsers como ya se hizo para `V5.x-R<N>` en V5.2. El baseline «3100/0/0» de Closure R3 es, por tanto, válido para el código pero no para el estado final comprometido. Suite completa de esta ronda: 3100 tests, **5 failures**, 0 errors, 132 skips (765 s); las 5 son exactamente las listadas.

## 12.1 Corrección autorizada de los tests
El humano autorizó corregir los tests señalados. Cambio mínimo: en los parsers de `tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py`, `tests/test_v4_r13_regression_and_security.py` y `tests/test_v4_r14_manuals_and_final_baseline.py` la regex pasó de `V([45])(?:\.(\d+))?-R(\d+)` a `V([45])(?:\.(\d+))?-(?:Closure-)?R(\d+)` (más un comentario). Sin tocar umbrales ni producción. Resultado: módulos afectados 189 tests OK; suite completa **3100 tests, 0 failures, 0 errors, 132 skips (676 s)**. Los 5 fallos quedaron resueltos.

## 13. Git
Árbol de trabajo con cambios sin commitear (documentación y estado únicamente) y los prompts sin versionar; no se hizo commit/push/tag. Producción intacta; único cambio fuera de documentación: los 3 archivos de test de §12.1.

## 14. Recomendación
Revisar y aprobar esta consolidación (incluidos los 3 tests corregidos) y autorizar el commit; luego iniciar **H1-R1 — AI-only contract, baseline validation and UX design**.

Estado: `POST_V5_DOCUMENTATION_CONSOLIDATION_READY_FOR_HUMAN_REVIEW` — `NEXT = H1_R1_AI_ONLY_CONTRACT_AND_UX_DESIGN`.
