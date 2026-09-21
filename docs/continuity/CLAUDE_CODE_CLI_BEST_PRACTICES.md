# Buenas prácticas para usar Claude Code / Claude CLI en LegacyMapper

## 1. Objetivo

Este documento resume cómo utilizar Claude Code de forma eficiente, reproducible y con menor consumo de tokens.

Las prácticas se basan en la experiencia real desarrollando LegacyMapper.

---

# 2. Modelo recomendado

Experiencia práctica:

```text
Sonnet 5 medium
```

funcionó bien durante V3 y V4.

Usarlo como modelo principal para:

- implementación;
- tests;
- documentación;
- correcciones;
- tareas mecánicas;
- refactors controlados.

Reservar Opus para:

- arquitectura compleja;
- contratos delicados;
- migraciones estructurales;
- diagnósticos que Sonnet no resuelve;
- revisiones críticas.

---

# 3. Regla de tres intentos

Si Claude falla por comprensión/modelo durante aproximadamente tres rondas:

```text
detener
→ revisar causa
→ cambiar modelo si corresponde
```

No seguir acumulando revisiones idénticas.

---

# 4. Prompts autocontenidos

Claude funciona mejor cuando el prompt contiene todo lo necesario.

Cada prompt debería incluir:

```text
Contexto
Objetivo
Rutas
Estado actual
Evidencia
Restricciones
Archivos permitidos
Archivos prohibidos
Tests
Resultado esperado
Estado final permitido
Next step
```

No depender de memoria implícita del agente.

---

# 5. Dar rutas exactas

Ejemplo correcto:

```text
Modificar:
legacy_documenter/context/ai_projection.py

Crear:
tests/test_v5_xxx.py

Resultado:
docs/V5/V5_X_RESULT.md
```

Evitar:

```text
busca dónde está la lógica y modifícala
```

salvo que el objetivo sea específicamente investigar.

---

# 6. Limitar exploración

Para reducir tokens:

```text
No leas archivos fuera de X/Y/Z salvo que sea necesario y documentes por qué.
```

Esto es especialmente importante en repos grandes.

---

# 7. Separar discovery de reasoning

No usar Claude para tareas que un script puede resolver mejor.

Crear herramientas para:

```text
inventario
dependency scan
hashing
test selection
metrics
context extraction
manifest
diff
```

Claude debería leer el resultado compacto.

---

# 8. Contexto compacto

En vez de pedir:

```text
lee todo el repositorio
```

preferir:

```text
usa:
- index
- manifest
- result docs
- targeted files
```

Un buen contexto pequeño supera a un contexto enorme mal seleccionado.

---

# 9. Usar documentos de handover

Antes de una ronda:

```text
estado actual
decisiones
deudas
scope
```

deben estar en Markdown.

Claude puede recuperar el contexto leyendo 2–5 documentos en vez de miles de mensajes previos.

---

# 10. No pedir análisis global innecesario

Evitar prompts como:

```text
revisa todo y mejora lo que consideres
```

Eso:

- consume tokens;
- expande scope;
- introduce cambios no deseados.

Preferir:

```text
revisa únicamente packing dentro de AiProjectionBuilder.package
```

---

# 11. Una tarea por prompt

Buenos prompts:

```text
diagnosticar
```

o:

```text
implementar
```

o:

```text
cerrar
```

Mal prompt:

```text
diagnostica, refactoriza, agrega plugin runtime, actualiza roadmap y cierra versión
```

---

# 12. Separar diagnóstico e implementación

Primero:

```text
DIAGNOSIS
```

Después, solo si está claro:

```text
CORRECTION
```

Esto evita corregir la causa equivocada.

---

# 13. Pedir evidencia

Cuando Claude haga una afirmación importante:

```text
mostrar datos
mostrar archivo
mostrar test
mostrar medición
```

No aceptar conclusiones vagas.

Ejemplo:

No:

```text
todos los records son grandes
```

Sí:

```text
35/40 >= 16000
5/40 < 16000
```

---

# 14. Pedir tests en la misma ronda

Una implementación sin tests genera rondas futuras.

El prompt de implementación debe exigir:

- unit tests;
- regression tests;
- determinism;
- runtime independence;
- synthetic fixture;
- real reproduction cuando corresponda.

---

# 15. Usar real repository solo donde aporta valor

No ejecutar IST completo por cada cambio menor.

Usar:

```text
unit tests
→ targeted integration
→ real repository gate
```

El piloto real debe reservarse para hitos relevantes.

---

# 16. No ejecutar provider real en tests

Tests normales:

```text
FakeLLMProvider
```

Provider real solo para:

```text
pilot
acceptance
end-to-end validation
```

Esto reduce coste, variabilidad y dependencia externa.

---

# 17. Distribución limpia para pilotos

Los pilotos reales deben ejecutarse desde una distribución limpia, no desde el checkout de desarrollo.

Ejemplo:

```text
C:\Tools\LegacyMapper
```

o distribución temporal.

Esto prueba exactamente el producto entregable.

---

# 18. Separar outputs

Nunca reutilizar una carpeta de output de un run anterior.

Usar:

```text
run_01
run_02
retry_01
```

Esto evita mezclar evidencias.

---

# 19. No permitir auto-approval

Los prompts de Claude deben preservar:

```text
PENDING_TECHNICAL_LEAD_REVIEW
```

y no aprobar propuestas automáticamente.

---

# 20. Mantener secretos fuera de prompts/resultados

Nunca pegar tokens completos en:

- prompts;
- documentos;
- commits;
- resultados.

Claude puede ejecutar:

```text
gh auth status
```

pero no debe persistir credenciales.

---

# 21. Pedir formato final fijo

Ejemplo:

```text
STATUS:
...

FILES MODIFIED:
...

TESTS:
...

RESTRICTIONS:
PASS/FAIL

NEXT STEP:
...
```

Esto hace comparables las rondas.

---

# 22. Estados finales limitados

El prompt debe indicar estados válidos.

Ejemplo:

```text
V5_2_READY_FOR_VALIDATION
V5_2_BLOCKED
```

No dejar que Claude invente estados.

---

# 23. No ejecutar siguiente ronda automáticamente

Una buena instrucción:

```text
Crear el siguiente prompt si corresponde, pero NO ejecutarlo.
```

Esto conserva el checkpoint humano.

---

# 24. Usar Git como frontera

Antes de una ronda importante:

```bat
git status
git branch --show-current
git rev-parse HEAD
```

Después:

```text
archivos modificados
archivos creados
diff relevante
```

No mezclar cambios ajenos.

---

# 25. Commits

Un cierre puede preparar commit si el working tree es claro.

No hacer push automático salvo autorización explícita.

Mantener commits por hito:

```text
Close V5.x ...
```

---

# 26. Evitar lectura repetida de archivos grandes

Si Claude ya produjo:

```text
manifest
index
diagnostic JSON
result doc
```

usar esos artifacts.

No pedirle releer cientos de MB.

---

# 27. Scripts auxiliares para ahorrar tokens

Crear herramientas como:

```text
tools/find_references.py
tools/run_targeted_tests.py
tools/build_context.py
tools/measure_flow_sizes.py
tools/compare_outputs.py
```

La idea:

```text
Python resume
→ Claude razona
```

---

# 28. Preferir outputs estructurados

Cuando Claude necesite producir información para otra ronda:

```json
{
  "status": "...",
  "metrics": {},
  "findings": [],
  "next_step": "..."
}
```

o Markdown con secciones fijas.

Esto reduce ambigüedad.

---

# 29. Evitar prompts demasiado abiertos

Mala instrucción:

```text
mejora el rendimiento
```

Buena:

```text
medir SCAN/EXTRACTION/FLOW_RESOLUTION en IST,
identificar top 3 costos,
no cambiar código,
crear resultado X
```

---

# 30. Primero medir, después optimizar

Para performance:

```text
baseline
→ profiler/metrics
→ diseño
→ implementación
→ comparación antes/después
```

No optimizar por intuición.

---

# 31. Model switching

Si Sonnet:

- no entiende un contrato;
- contradice repetidamente invariantes;
- genera parches circulares;

después de ~3 intentos:

```text
pasar a Opus
```

No aumentar indefinidamente el tamaño del prompt esperando que el mismo modelo resuelva el problema.

---

# 32. Claude no debe decidir scope solo

Claude puede proponer.

El prompt debe fijar:

```text
IN
OUT
DO NOT MODIFY
```

Esto evita scope creep.

---

# 33. Architecture rounds

Para arquitectura compleja pedir:

```text
alternativas
trade-offs
compatibilidad
migración
tests
rollback
```

No permitir implementación hasta aprobar contrato.

---

# 34. Mechanical rounds

Para tareas mecánicas usar Sonnet y comandos exactos.

Ejemplos:

```text
rename
move
add tests
update docs
wire CLI
```

No gastar Opus en estos casos.

---

# 35. Uso recomendado en V5

Patrón:

```text
R0 Empirical Baseline
   Claude lee resultados compactos

R1 Contract & Design
   Sonnet u Opus según complejidad

R2 Implementation
   Sonnet medium

R3 Verification
   Sonnet medium + Python/tests

R4 Closure
   Sonnet medium
```

---

# 36. Template para un prompt eficiente

```text
# CONTEXTO
<solo hechos necesarios>

# OBJETIVO
<una sola responsabilidad>

# RUTAS
<paths exactos>

# EVIDENCIA
<result docs / metrics>

# IMPLEMENTAR
<alcance>

# NO MODIFICAR
<lista explícita>

# TESTS
<qué ejecutar>

# RESULTADO
<archivo a crear>

# ESTADOS PERMITIDOS
<lista>

# NEXT STEP
Crear pero no ejecutar el siguiente prompt.
```

---

# 37. Señales de que el prompt es demasiado grande

Si el prompt contiene:

- demasiadas features;
- varios rediseños;
- varias etapas independientes;
- muchas decisiones aún abiertas;

dividir antes de ejecutar.

---

# 38. Señales de que Claude está gastando tokens de más

- vuelve a explorar carpetas ya indexadas;
- relee archivos sin necesidad;
- explica repetidamente el mismo contexto;
- genera documentación redundante;
- ejecuta suites completas después de cada cambio pequeño;
- intenta interpretar outputs que Python puede resumir.

Corregir proceso, no solo cambiar modelo.

---

# 39. Objetivo operativo

El flujo ideal es:

```text
Python descubre
        ↓
Claude recibe contexto compacto
        ↓
Claude decide/modifica
        ↓
Python valida
        ↓
Claude documenta resultado
        ↓
humano aprueba siguiente paso
```

Ese patrón produjo los mejores resultados en LegacyMapper.
