# LegacyMapper V5.3 — R4 Closure + Commit + Push

## 1. Objetivo
Cerrar formalmente V5.3 — Incremental Engine & Cache.

Esta ronda debe:
- consolidar la aprobación humana de R3;
- cerrar V5.3 documental y contractualmente;
- actualizar `PROJECT_STATE.json`;
- actualizar continuidad;
- incluir el informe pendiente R2.9.1;
- incluir prompt e informe R3;
- generar el informe final R4;
- crear UN commit local de cierre;
- hacer push de `main` a `origin/main`;
- verificar que el respaldo remoto quedó actualizado.

NO iniciar V5.4.

## 2. Estado de partida
Checkpoint versionado más reciente:

`aa7db0db6c77d7ec8a1b15f50e33bf176d948bcd`

Estado esperado:
- rama `main`;
- `main` 6 commits ahead de `origin/main` antes del cierre;
- backup `backup/v5.3-pre-worktree-cleanup`
  → `2cb317fe5ae3dd2cbad1f865b1faee4a50a99569`;
- R2 completo técnicamente;
- R3 aprobado humanamente;
- R3: `V5_3_R3_READY_FOR_HUMAN_REVIEW`;
- V5.3 todavía abierta;
- R4 no iniciada.

Defaults aprobados para V5.3:
- `cache-mode=auto`
- `verify-cache=fast`
- `trust-mtime=false`
- `incremental-max-changed-ratio=None`

Estado adicional:
`CHANGED_RATIO_DEFAULT_DEFERRED`

Pendientes esperados:
- `docs/V5/V5_3_R2_9_1_GIT_CHECKPOINT.md`
- `docs/V5/V5_3_R3_VERIFICATION_REAL_REGRESSION.md`
- `prompts/V5/V5_3_R3_VERIFICATION_REAL_REGRESSION.md`
- `tests/test_v5_3_r3_verification.py`
- cambios en `PROJECT_STATE.json`
- cambios de continuidad

## 3. Autorización Git
El usuario autoriza explícitamente en esta ronda:
- revisar Git;
- staging explícito;
- crear UN commit local;
- hacer push de `main` a `origin/main`.

NO autoriza:
- tag;
- release;
- force push;
- amend;
- rebase;
- reset destructivo;
- clean;
- eliminación de ramas;
- iniciar V5.4.

Si el push normal es rechazado por divergencia remota:
- NO usar force push;
- detenerse;
- informar el motivo;
- estado final `V5_3_R4_PUSH_BLOCKED`.

## 4. Fuentes obligatorias
Leer antes de actuar:
- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.md`
- `docs/V5/V5_3_R2_9_1_GIT_CHECKPOINT.md`
- `docs/V5/V5_3_R3_VERIFICATION_REAL_REGRESSION.md`
- `PROJECT_STATE.json`
- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`
- `AGENTS.md`
- `CLAUDE.md`

R1 sigue siendo autoridad contractual.

## 5. Cierre técnico de V5.3
Registrar formalmente que V5.3 entrega:
- File State persistente;
- semantic/raw hashes;
- extraction cache shardeada;
- compatibilidad/versionado/fingerprints;
- manifest-last seguro;
- write-skip de outputs;
- HydrationView compartida;
- scope analysis conservador;
- RUN_METRICS persistido;
- CLI de cache;
- verify fast/hash;
- cache interna/externa;
- refresh/off/auto;
- changed ratio opt-in;
- comparador full vs incremental;
- recuperación ante corrupción/incompatibilidad;
- seguridad de paths;
- junction/reparse validado;
- regresión real IST;
- determinismo/equivalencia canónica.

No declarar funcionalidades no implementadas.

## 6. Deuda final de V5.3
Preservar como no bloqueante:

### FUTURE_PHASE
- partial resolver recomputation;
- stage skipping;
- flow cache;
- projection cache;
- `artifacts.json`;
- refactor `full_pipeline.py`;
- unificación de atomic writers.

### OBSERVATION
- `repository.json` no determinista;
- `trust-mtime` inseguro opt-in;
- changed ratio default diferido;
- scope conservador.

No convertir deuda futura en requisito de cierre.

## 7. Validaciones mínimas de R4
R4 no debe repetir IST ni la suite completa salvo que se cambie runtime.

Ejecutar:
- tests dirigidos R3;
- tests R2.9 de calibración/comparador;
- `git diff --check`.

Mínimo recomendado:

`python -X utf8 -m unittest tests.test_v5_3_r3_verification tests.test_v5_3_r2_9_incremental_calibration`

Si cualquier archivo en `legacy_documenter/` cambia durante R4:
- detener cierre;
- ejecutar suite completa;
- documentar motivo.

Idealmente R4 no modifica runtime.

## 8. PROJECT_STATE.json
Actualizar al cierre formal:
- current_version = V5.3;
- status = `V5_3_CLOSED`;
- latest_completed_round = V5.3-R4;
- latest_approved_round = V5.3-R3;
- round_status = CLOSED;
- next_version = V5.4;
- next_round = V5.4-R1;
- R3 verification = approved;
- R4 closure = completed;
- R2 complete = true;
- V5.3 closed = true;
- defaults finales preservados;
- changed ratio default deferred;
- tests baseline actualizados;
- tag = null si el esquema lo permite.

No inventar tag.

## 9. Continuidad
Actualizar:
- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`

Registrar:
- R2.9.1 checkpoint;
- R3 aprobado;
- R4 cerrado;
- V5.3 CLOSED;
- V5.4 autorizado como siguiente versión;
- nuevo modelo de trabajo para V5.4:
  - R1 Integrated Delivery
  - R2 Targeted Corrections solo si es necesaria
  - R3 Final Verification & Closure
  - máximo objetivo: 3 rondas por versión
  - un objetivo coherente por ronda, no micro-rondas innecesarias.

Preservar historia previa.

## 10. Documento R4
Crear:
`docs/V5/V5_3_R4_CLOSURE.md`

Debe incluir:
1. Objetivo.
2. Estado inicial.
3. Aprobaciones humanas.
4. Resumen R0/R1/R2/R3.
5. Capacidades finales V5.3.
6. Defaults finales.
7. Evidencia de equivalencia.
8. Evidencia de recuperación/fallback.
9. Evidencia de determinismo.
10. Evidencia IST.
11. Tests finales.
12. Deuda final.
13. Riesgos aceptados.
14. PROJECT_STATE.
15. Continuidad.
16. Git pre-commit.
17. Commit.
18. Push.
19. Estado remoto.
20. Próxima versión V5.4.
21. Estado final.

## 11. Staging
Antes:
- `git status --short`
- `git diff --stat`
- `git diff --check`

Revisar cada archivo.

NO usar `git add .` sin inspección.

Agregar por rutas explícitas.

Esperados:
- `PROJECT_STATE.json`
- documentos de continuidad
- `docs/V5/V5_3_R2_9_1_GIT_CHECKPOINT.md`
- `docs/V5/V5_3_R3_VERIFICATION_REAL_REGRESSION.md`
- `prompts/V5/V5_3_R3_VERIFICATION_REAL_REGRESSION.md`
- `tests/test_v5_3_r3_verification.py`
- `docs/V5/V5_3_R4_CLOSURE.md`
- prompt R4 si está dentro del repo
- cualquier archivo exclusivamente documental creado por esta ronda.

No incluir outputs locales/IST/cache.

## 12. Commit de cierre
Crear UN commit local.

Mensaje recomendado:
`chore(v5.3): close incremental engine phase`

No amend.

Registrar:
- hash completo;
- hash corto;
- padre;
- archivos;
- stat.

## 13. Push autorizado
Después del commit y solo si:
- tests dirigidos verdes;
- `git diff --check` PASS;
- staging correcto;
- commit creado;
- working tree coherente.

Ejecutar:
`git push origin main`

No usar `--force`.

Si requiere autenticación y falla por credenciales:
- no intentar workarounds inseguros;
- documentar;
- estado `V5_3_R4_PUSH_BLOCKED`.

## 14. Verificación remota
Después de push exitoso:
- verificar exit code 0;
- consultar `git status -sb`;
- consultar `git log -1 --oneline`;
- consultar `git rev-parse HEAD`;
- comparar `git rev-parse origin/main` con `HEAD`.

Esperado:
`origin/main == HEAD`

No hacer fetch adicional salvo que sea necesario para verificar el push y no altere historia.

## 15. Tag
NO crear tag.

El usuario autorizó commit + push, no tag.

Registrar:
`tag: NOT_CREATED_BY_INSTRUCTION`

## 16. Informe con hash posterior
Si `docs/V5/V5_3_R4_CLOSURE.md` necesita contener el hash definitivo del commit y por ello el documento cambia después del commit:

Preferencia:
- preparar el documento antes del commit sin auto-referenciar el hash completo;
- obtener hash;
- registrar el hash en salida de consola/result summary posterior.

NO hacer amend ni crear un segundo commit solo para auto-documentar el primero sin autorización explícita.

## 17. Estado Git final esperado
Después del push:
- branch `main`;
- `HEAD == origin/main`;
- 0 commits ahead;
- no push pendiente;
- backup branch intacto;
- sin tag nuevo;
- working tree limpio o únicamente reporte administrativo posterior no versionado.

## 18. Estado final permitido
Si cierre, commit y push pasan:

`V5_3_CLOSED`

y:

`V5_3_R4_PUSHED_TO_ORIGIN_MAIN`

Si cierre/commit pasan pero push falla:

`V5_3_R4_PUSH_BLOCKED`

Si aparece regresión o cambio runtime inesperado:

`V5_3_R4_BLOCKED`

## 19. Próximo paso
No iniciar V5.4 en esta ronda.

Solo registrar:
`V5_4_READY_TO_START`

La próxima ronda V5.4 debe seguir el nuevo modelo acordado:
- R1 — Integrated Delivery;
- R2 — Targeted Corrections solo si hace falta;
- R3 — Final Verification & Closure;
- máximo objetivo de tres rondas.

## 20. Criterio de cierre
V5.3 se considera cerrada si:
- R3 aprobado humanamente;
- PROJECT_STATE actualizado;
- continuidad actualizada;
- documento R4 creado;
- tests dirigidos verdes;
- no cambios runtime inesperados;
- commit local creado;
- push normal a `origin/main` exitoso;
- `origin/main == HEAD`;
- no tag creado;
- V5.3 marcada CLOSED;
- V5.4 registrada READY_TO_START.

Detenerse para revisión humana final.
