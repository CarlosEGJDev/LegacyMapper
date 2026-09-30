# PRE-V5.1 Test Baseline Gate — Result

## STATUS

`PRE_V5_1_GATE_BLOCKED`

Ronda de corrección de tests. Se aplicó exactamente la Opción A a los 4 tests históricos clasificados por R2/R2A/R3 y quedaron verdes de forma estable. No se modificó producción, CLI, providers ni `PROJECT_STATE.json`. No se modificaron baselines congelados. No se implementó V5.1.

El gate queda **bloqueado**, no por la corrección aplicada (que es correcta y estable), sino porque la ejecución de la suite completa (tarea 4 del prompt) reveló una recurrencia del riesgo intermitente ya documentado `test_deterministic_run_then_ai_enabled_rerun_same_output` (V4.2-R6), que además arrastró fallos intermitentes adicionales en el mismo módulo (`tests/test_v4_2_r6_robustness_recovery_security_and_approval_surface.py`) y en un módulo relacionado (`tests/test_v4_2_r7_synthetic_full_fixture.py`) al repetir la ejecución. Esto no es un fallo distinto de los 4 originales en el sentido del punto 1 del prompt (ya confirmados y corregidos), pero sí impide declarar "suite completa verde" de forma fiable, que es el gate 2 exigido por R3. Corregir esa causa raíz excede el alcance autorizado de esta ronda (no modificar producción, no ampliar scope), así que se documenta y se detiene aquí.

## ROOT CAUSE

**De los 4 tests originales (resuelto):** las 3 aserciones `provider_calls == 0` / `real_llm_calls == 0` contra `PROJECT_STATE.json` **vivo**, y la comparación byte-a-byte de esos mismos dos campos en `test_baseline_matches_on_disk_artifact`, asumían que esos campos permanecían en 0 indefinidamente. `PROJECT_STATE.json` avanzó legítimamente a `provider_calls=1`/`real_llm_calls=1` en el commit `44e2a94` (piloto real de IA de V4.3, ya autorizado). La causa raíz es exactamente la identificada por R2/R2A/R3: un conflicto entre "invariante histórica de fase" y "estado acumulado que avanza", no una regresión de producción.

**Del bloqueo del gate (nuevo, no atribuible a esta ronda):** al ejecutar `python -m unittest discover -s tests` dos veces seguidas sin ningún cambio entre ejecuciones, aparecieron fallos intermitentes distintos en cada corrida, todos dentro de las pruebas de rerun/determinismo de la suite de robustez del pipeline con IA:
- 1ª corrida: `test_deterministic_run_then_ai_enabled_rerun_same_output` — `FAIL`.
- 2ª corrida: `test_deterministic_run_then_ai_enabled_rerun_same_output`, `test_successful_run_then_successful_rerun`, `test_rerun_into_the_same_output_remains_safe` — `FAIL`; `test_ai_failure_after_prior_successful_ai_run_produces_a_fresh_no_proposals_envelope` — `ERROR`.

Ejecutado en aislamiento, `test_deterministic_run_then_ai_enabled_rerun_same_output` pasa (`OK`, 1 test, 0.9 s). El patrón (pasa aislado, falla de forma variable dentro de la suite completa, con miembros distintos del mismo grupo de tests de rerun cada vez) es consistente con el riesgo ya registrado en `PROJECT_STATE.json` (`known_risks.r6_intermittent_test`) y en `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md` (riesgo 9: "sigue siendo trigger de investigación"). No se investigó la causa técnica (contención de recursos temporales entre tests de rerun, orden de ejecución, limpieza de directorios de salida compartidos, u otra); hacerlo requeriría tocar producción o tests fuera del alcance autorizado de esta ronda.

## FILES MODIFIED

- `tests/test_v4_r13_regression_and_security.py` — `RepositoryContinuityStateTests.test_project_state_no_ai_or_provider_calls_recorded`: se eliminó la aserción `provider_calls == 0` / `real_llm_calls == 0` contra el estado vivo; se conserva `ai_knowledge_generated == False`; se añadió comentario explicando la decisión y remitiendo a la cobertura congelada.
- `tests/test_v4_r14_manuals_and_final_baseline.py`:
  - `EntryGateAndContinuityTests.test_project_state_readiness_ready`: se eliminó la misma aserción contra el estado vivo; se conserva `readiness`, `ai_knowledge_allowed`, `ai_knowledge_generated`.
  - `NoProviderOrLlmCallsTests.test_project_state_confirms_zero_calls`: se redirigió a verificar `provider_calls == 0` / `real_llm_calls == 0` contra el artefacto congelado (`BASELINE_PATH`) en vez del estado vivo, preservando la invariante histórica en su ubicación correcta (ya cubierta también por `BaselineJsonValidityTests.test_provider_and_llm_calls_zero`, sin cambios).
  - `DeterminismTests.test_baseline_matches_on_disk_artifact`: se añadió `provider_calls`/`real_llm_calls` al conjunto de campos normalizados (excluidos de la comparación byte-a-byte), siguiendo el patrón `REG-002` ya usado para `latest_approved_round`/`test_count`/conteos de módulos; se añadió la comprobación "nunca retrocede" (`assertGreaterEqual`) para ambos campos frente al snapshot congelado.

Ningún otro archivo fue modificado. `PROJECT_STATE.json` no se tocó (`git diff --stat -- PROJECT_STATE.json` vacío). No se modificó `output/v4_r14/V4_FINAL_BASELINE.json` ni ningún otro artefacto congelado.

## TARGETED TEST RESULT

Confirmación previa a la corrección (`python -m unittest tests.test_v4_r13_regression_and_security tests.test_v4_r14_manuals_and_final_baseline`): 92 tests, **4 fallos exactos** (los clasificados por R2/R2A/R3), 0 errores. Coincide con lo esperado; no aparecieron fallos distintos, por lo que se procedió sin STOP.

Tras aplicar la Opción A, reejecución del mismo comando:

```text
Ran 92 tests in 1.646s

OK
```

**0 failures, 0 errors.** Reejecutado una segunda vez para descartar que fuera una corrida afortunada: mismo resultado, estable.

## FULL SUITE RESULT

`python -m unittest discover -s tests`, primera corrida:

```text
Ran 2169 tests in 219.267s

FAILED (failures=1, skipped=132)
```

Único fallo: `test_deterministic_run_then_ai_enabled_rerun_same_output` (`tests/test_v4_2_r6_robustness_recovery_security_and_approval_surface.py`).

Segunda corrida (sin cambios entre medio), para verificar reproducibilidad:

```text
Ran 2169 tests in 244.220s

FAILED (failures=3, errors=1, skipped=132)
```

Fallos: `test_deterministic_run_then_ai_enabled_rerun_same_output`, `test_successful_run_then_successful_rerun` (mismo módulo); `test_rerun_into_the_same_output_remains_safe` (`test_v4_2_r7_synthetic_full_fixture.py`). Error: `test_ai_failure_after_prior_successful_ai_run_produces_a_fresh_no_proposals_envelope`.

**Conteo total de tests sin cambios:** 2169 tests, 132 skips en ambas corridas — coincide exactamente con el baseline esperado por R3 (`2169 tests / 132 skips`). Ninguno de los 4 tests originales de la Opción A reapareció en ninguna de las dos corridas completas: la corrección es estable incluso dentro de la suite completa. Los fallos observados son exclusivamente del grupo de rerun/determinismo del pipeline con IA, no relacionados con `provider_calls`/`real_llm_calls`/`PROJECT_STATE.json`.

## PROJECT_STATE CHECK

`PROJECT_STATE.json` no fue editado en ningún momento de esta ronda (verificado con `git diff` antes y después de los cambios: sin diferencias). `provider_calls`/`real_llm_calls` permanecen en `1`/`1`, reflejando el piloto real de V4.3 ya autorizado; ningún test nuevo o modificado exige que retrocedan a `0`.

## BASELINE CHECK

`output/v4_r14/V4_FINAL_BASELINE.json` no fue modificado. `BaselineJsonValidityTests.test_provider_and_llm_calls_zero` (línea `216`) sigue verificando `provider_calls == 0` / `real_llm_calls == 0` directamente sobre ese artefacto congelado, sin cambios, y pasa. `DeterminismTests.test_baseline_matches_on_disk_artifact` sigue comparando el baseline reconstruido contra el artefacto en disco, ahora normalizando `provider_calls`/`real_llm_calls` además de los campos ya normalizados (`latest_approved_round`, `test_count`, conteos de módulos de mantenibilidad), con la comprobación adicional de que esos dos campos nunca retroceden respecto al snapshot congelado.

## PRE-V5.1 GATE STATUS

| Gate (de R3) | Estado |
|---|---|
| 1. Aplicar Opción A a los 4 tests rojos | **CUMPLIDO** — los 4 tests corregidos, verdes y estables en ejecuciones repetidas. |
| 2. Suite completa verde | **NO CUMPLIDO** — 2169 tests / 132 skips confirmados (conteo correcto), pero con fallos intermitentes recurrentes ajenos a la Opción A (1 fallo en la 1ª corrida, 3 fallos + 1 error en la 2ª), todos dentro del grupo de tests de rerun/determinismo con IA. No se obtuvo una corrida limpia de 0 failures/0 errors en esta ronda. |
| 3. No editar retroactivamente `PROJECT_STATE.json` | **CUMPLIDO** — sin cambios, verificado con `git diff`. |
| 4. Mantener la arquitectura consolidada sin nuevos conflictos | **CUMPLIDO** — ningún cambio de contrato; solo se tocaron aserciones de tests históricos, dentro del alcance autorizado. |

Con el gate 2 no satisfecho, el resultado global de esta ronda es `PRE_V5_1_GATE_BLOCKED`. El bloqueo es específico: no afecta a la corrección de la Opción A (gates 1, 3 y 4 completos), sino a la exigencia de "suite completa verde" frente a un riesgo intermitente preexistente y ya documentado antes de esta ronda.

## RISKS

1. **Riesgo confirmado como recurrente:** `test_deterministic_run_then_ai_enabled_rerun_same_output` (V4.2-R6), previamente `NON_REPRODUCIBLE_AS_OF_V4.2_FORMAL_CLOSURE` en `PROJECT_STATE.json`, reapareció en esta ronda. R1 (`docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md`, riesgo 9) ya advertía que cualquier recurrencia debe tratarse como disparador de investigación explícita — esta ronda deja constancia de esa recurrencia, sin investigarla (fuera de alcance).
2. **Alcance ampliado del síntoma:** en la segunda corrida el problema no se limitó al test históricamente conocido; afectó a otros 3 tests del mismo grupo de rerun/determinismo (`test_successful_run_then_successful_rerun`, `test_rerun_into_the_same_output_remains_safe`, y un error en `test_ai_failure_after_prior_successful_ai_run_produces_a_fresh_no_proposals_envelope`), sugiriendo una causa compartida (posible contención de recursos temporales, orden/aislamiento entre tests de rerun, o limpieza de directorios de salida) más amplia que el síntoma puntual de V4.2-R6.
3. **No se determinó la causa técnica exacta** de la intermitencia en esta ronda; investigarla requeriría inspeccionar/posiblemente modificar producción o fixtures de test, fuera del alcance autorizado explícitamente aquí.
4. **Bloqueo de V5.1:** mientras el gate 2 no se cumpla con una corrida limpia y reproducible, V5.1 no puede iniciarse formalmente según los PRE-V5.1 GATES de R3, aunque la corrección de la Opción A (el objetivo específico de esta ronda) ya esté completa.

## NEXT STEP

No se crea el prompt de V5.1 ni ningún otro prompt siguiente, por quedar en `PRE_V5_1_GATE_BLOCKED` (y porque, aun si el gate 2 se hubiera cumplido, la regla de la ronda exige esperar aprobación humana).

Queda pendiente de decisión y aprobación humana una ronda separada, explícitamente autorizada, para investigar y corregir la causa raíz de la intermitencia en `tests/test_v4_2_r6_robustness_recovery_security_and_approval_surface.py` / `tests/test_v4_2_r7_synthetic_full_fixture.py` antes de que el PRE-V5.1 GATE pueda declararse `PASSED`.
