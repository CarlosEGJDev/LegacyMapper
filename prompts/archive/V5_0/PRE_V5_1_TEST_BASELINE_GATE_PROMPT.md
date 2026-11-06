# LegacyMapper — PRE-V5.1 Test Baseline Gate

## MODELO RECOMENDADO

Claude Sonnet 5, medium.

---

# OBJETIVO

Cumplir el gate previo obligatorio a V5.1 definido en:

```text
docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md
```

Esta ronda corrige exclusivamente los 4 tests históricos clasificados como obsoletos por R2/R2A y verifica que la suite completa vuelva a quedar verde.

NO implementa V5.1.

---

# ROOT

```text
C:\dev\LegacyMapper
```

---

# LEE PRIMERO

```text
CLAUDE.md
AGENTS.md
PROJECT_STATE.json
docs/V5/V5_0_R2_CONTRACT_VALIDATION.md
docs/V5/V5_0_R2A_CONTRACT_CORRECTIONS.md
docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md
```

---

# ESTADO DE PARTIDA

```text
V5_0_R3_READY_FOR_PRE_V5_1_GATE
```

R3 define como PRE-V5.1 GATES obligatorios:

1. aplicar la Opción A a los 4 tests rojos;
2. suite completa verde;
3. no editar retroactivamente `PROJECT_STATE.json`;
4. mantener la arquitectura consolidada sin nuevos conflictos.

---

# ALCANCE

Modificar únicamente los tests históricos afectados por la decisión Opción A.

Archivos previstos:

```text
tests/test_v4_r13_regression_and_security.py
tests/test_v4_r14_manuals_and_final_baseline.py
```

No modificar producción.

No modificar `PROJECT_STATE.json`.

No modificar baselines históricos congelados.

---

# DECISIÓN APROBADA — OPTION A

Aplicar exactamente la decisión fijada por R2A/R3:

1. `PROJECT_STATE.json` representa estado/historia acumulada y puede avanzar.
2. La invariante histórica:
   ```text
   provider_calls == 0
   real_llm_calls == 0
   ```
   pertenece al baseline congelado de V4:
   ```text
   output/v4_r14/V4_FINAL_BASELINE.json
   ```
3. Los tests que leen `PROJECT_STATE.json` vivo no deben seguir afirmando que esos valores permanecen en 0.
4. `test_baseline_matches_on_disk_artifact` debe normalizar también:
   ```text
   provider_calls
   real_llm_calls
   ```
   siguiendo el patrón REG-002 ya usado para otros campos que avanzan legítimamente.

---

# TAREA

## 1. Confirmar los 4 fallos exactos

Antes de modificar tests, ejecutar:

```text
python -m unittest tests.test_v4_r13_regression_and_security tests.test_v4_r14_manuals_and_final_baseline
```

Confirmar que siguen siendo exactamente los 4 fallos clasificados.

Si aparecen fallos distintos:

```text
STOP
```

y documentarlos. No ampliar scope.

---

## 2. Aplicar Opción A

Modificar únicamente las aserciones afectadas.

Objetivo esperado:

- eliminar la expectativa histórica `provider_calls == 0` sobre `PROJECT_STATE.json` vivo;
- preservar esa invariante contra el baseline congelado, donde ya existe cobertura;
- normalizar `provider_calls` y `real_llm_calls` en `test_baseline_matches_on_disk_artifact`.

No debilitar otros asserts.

No convertir tests en triviales.

No usar skips para ocultar el problema.

---

## 3. Ejecutar tests dirigidos

Reejecutar:

```text
python -m unittest tests.test_v4_r13_regression_and_security tests.test_v4_r14_manuals_and_final_baseline
```

Esperado:

```text
0 failures
0 errors
```

---

## 4. Ejecutar suite completa

Ejecutar:

```text
python -m unittest discover -s tests
```

Gate esperado:

```text
0 failures
0 errors
132 skips esperados
```

Si cambia el conteo total de tests por la modificación, documentarlo.

No editar `PROJECT_STATE.json` para forzar coincidencia.

---

# REGLA DE DOCUMENTACIÓN

Claude NO debe crear archivos `.md` por iniciativa propia.

En esta ronda solo está autorizado a crear:

```text
docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md
```

No crear prompts siguientes.

No crear R1A/R1B.

No crear FIX_NOTES, PATCH_RESULT, TODO_FIX ni diagnósticos separados.

---

# OUTPUT OBLIGATORIO

Crear:

```text
docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md
```

Debe contener:

```text
STATUS
ROOT CAUSE
FILES MODIFIED
TARGETED TEST RESULT
FULL SUITE RESULT
PROJECT_STATE CHECK
BASELINE CHECK
PRE-V5.1 GATE STATUS
RISKS
NEXT STEP
```

---

# ESTADOS PERMITIDOS

Solo:

```text
PRE_V5_1_GATE_PASSED
PRE_V5_1_GATE_BLOCKED
```

---

# RESTRICCIONES

NO:

- modificar producción;
- modificar `PROJECT_STATE.json`;
- modificar artefactos congelados V4;
- tocar CLI;
- tocar providers;
- implementar V5.1;
- ejecutar IA real;
- ejecutar full IST;
- crear documentación auxiliar;
- iniciar V5.1.

---

# NEXT STEP

Si queda:

```text
PRE_V5_1_GATE_PASSED
```

NO crear el prompt de V5.1.

Esperar aprobación humana.

---

# PRINCIPIO FINAL

```text
baseline limpio
→ suite verde
→ V5.1
```
