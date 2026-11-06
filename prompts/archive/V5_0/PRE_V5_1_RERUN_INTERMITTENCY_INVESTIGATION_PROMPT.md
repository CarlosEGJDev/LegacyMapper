# LegacyMapper — PRE-V5.1 Rerun Intermittency Investigation

## MODELO RECOMENDADO

Claude Sonnet 5, medium.

Usar Opus solo si existe un bloqueo técnico real que Sonnet no resuelva tras aproximadamente tres iteraciones bien acotadas.

---

# OBJETIVO

Investigar y corregir la causa raíz de la intermitencia confirmada durante el PRE-V5.1 Test Baseline Gate, sin ampliar innecesariamente el alcance.

Estado de partida:

```text
PRE_V5_1_GATE_BLOCKED
```

La Opción A ya fue aplicada correctamente y los 4 tests históricos originales quedaron verdes y estables.

El bloqueo actual proviene exclusivamente de fallos intermitentes en tests de rerun/determinismo del pipeline con IA.

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
docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md
docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md
PROJECT_STATE.json
```

Después leer solo los tests/módulos estrictamente relacionados con los fallos observados.

---

# SÍNTOMAS CONFIRMADOS

Durante dos ejecuciones consecutivas de la suite completa:

Primera corrida:

```text
2169 tests
1 failure
132 skips
```

Fallo:

```text
test_deterministic_run_then_ai_enabled_rerun_same_output
```

Segunda corrida:

```text
2169 tests
3 failures
1 error
132 skips
```

Afectados:

```text
test_deterministic_run_then_ai_enabled_rerun_same_output
test_successful_run_then_successful_rerun
test_rerun_into_the_same_output_remains_safe
test_ai_failure_after_prior_successful_ai_run_produces_a_fresh_no_proposals_envelope
```

El test histórico:

```text
test_deterministic_run_then_ai_enabled_rerun_same_output
```

pasa en aislamiento.

Esto sugiere interferencia entre tests, estado compartido, limpieza incompleta, recursos temporales, orden de ejecución o lifecycle compartido.

NO asumir la causa sin evidencia.

---

# ARCHIVOS DE TEST PRINCIPALES

Investigar primero:

```text
tests/test_v4_2_r6_robustness_recovery_security_and_approval_surface.py
tests/test_v4_2_r7_synthetic_full_fixture.py
```

Luego seguir solo las llamadas de producción necesarias.

---

# TAREA

## 1. Reproducir de forma controlada

Ejecutar individualmente los tests afectados.

Luego ejecutar pequeños grupos:

```text
2 tests
3 tests
módulo R6 completo
módulo R7 completo
R6 + R7
```

Variar orden cuando sea útil.

Objetivo:

identificar la secuencia mínima que reproduce el fallo.

No empezar modificando código.

---

## 2. Capturar evidencia de interferencia

Comparar antes/después de cada test relevante:

- directorios temporales;
- output dirs reutilizados;
- variables de entorno;
- registry/config globals;
- caches/global module state;
- provider registry state;
- fake provider state;
- monkeypatches;
- cwd;
- archivos persistentes;
- cleanup/finalizers;
- asyncio state;
- recursos abiertos;
- contenido previo del mismo output;
- orden de stages/result files.

Si existe estado global mutable, documentar:

```text
owner
setter
reader
reset mechanism
```

---

## 3. Determinar si la causa está en tests o producción

Clasificar la causa raíz en una sola categoría principal:

```text
TEST_ISOLATION_BUG
PRODUCTION_RERUN_BUG
SHARED_GLOBAL_STATE
TEMP_OUTPUT_COLLISION
PROVIDER_LIFECYCLE
NONDETERMINISTIC_ORDER
OTHER
```

Puede haber factores secundarios, pero debe existir una causa principal sustentada por evidencia.

---

## 4. Aplicar el arreglo mínimo

Solo después de identificar la causa.

Reglas:

- si es aislamiento de tests, corregir fixtures/setup/teardown;
- si es producción real, corregir producción con el cambio mínimo;
- no debilitar asserts;
- no agregar skips;
- no convertir la prueba en tolerante a comportamiento incorrecto;
- no borrar evidencia útil antes de inspeccionarla;
- no tocar V5.1.

---

## 5. Validación dirigida

Después del fix:

1. ejecutar cada test afectado individualmente;
2. ejecutar R6 completo;
3. ejecutar R7 completo;
4. ejecutar R6+R7 juntos varias veces.

Mínimo recomendado:

```text
3 ejecuciones consecutivas de R6+R7
```

todas verdes.

---

## 6. Validación de suite completa

Solo cuando los grupos anteriores sean estables:

```text
python -m unittest discover -s tests
```

Ejecutar al menos dos veces consecutivas.

Gate esperado en ambas:

```text
2169 tests
0 failures
0 errors
132 skips
```

Si el conteo cambia por tests añadidos legítimamente, documentarlo.

---

# REGLA DE DOCUMENTACIÓN

Claude NO debe crear `.md` adicionales por iniciativa propia.

Solo puede crear:

```text
docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md
```

No crear prompt siguiente.

No crear FIX_NOTES, PATCH_RESULT, R1A/R1B, TODO ni diagnósticos separados.

---

# OUTPUT OBLIGATORIO

Crear:

```text
docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md
```

Debe contener:

```text
STATUS
REPRODUCTION
ROOT CAUSE
CLASSIFICATION
DESIGN
FILES MODIFIED
TARGETED TESTS
R6/R7 STABILITY TESTS
FULL SUITE RESULTS
PROJECT_STATE CHECK
RUNTIME IMPACT
RISKS
PRE-V5.1 GATE RECOMMENDATION
NEXT STEP
```

---

# ESTADOS PERMITIDOS

Solo:

```text
PRE_V5_1_RERUN_ISSUE_RESOLVED
PRE_V5_1_RERUN_ISSUE_NOT_REPRODUCED
PRE_V5_1_RERUN_ISSUE_BLOCKED
```

`NOT_REPRODUCED` no equivale automáticamente a gate aprobado.

---

# RESTRICCIONES

NO:

- implementar V5.1;
- cambiar arquitectura V5.0;
- modificar PROJECT_STATE.json retroactivamente;
- alterar baselines congelados;
- ocultar fallos con skips;
- relajar asserts sin causa demostrada;
- ejecutar IA real;
- ejecutar full IST;
- crear documentación auxiliar.

---

# NEXT STEP

Si queda:

```text
PRE_V5_1_RERUN_ISSUE_RESOLVED
```

y existen dos suites completas consecutivas verdes, NO crear prompt de V5.1.

Esperar aprobación humana para declarar:

```text
PRE_V5_1_GATE_PASSED
```

y comenzar V5.1.

---

# PRINCIPIO FINAL

```text
reproducir
→ aislar
→ demostrar causa
→ corregir mínimo
→ repetir
→ suite estable
```
