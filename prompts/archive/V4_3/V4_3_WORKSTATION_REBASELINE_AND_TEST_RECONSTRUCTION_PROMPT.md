# PROMPT — V4.3 WORKSTATION REBASELINE & TEST RECONSTRUCTION

## 0. Contexto

Se cambió de notebook/PC de trabajo.

Rutas vigentes:

- LegacyMapper:
  `C:\dev\LegacyMapper`

- Aplicación legacy real Operacional:
  `C:\inetpub\wwwroot\2010\IST\Operacional`

En el cambio de equipo se copió el repositorio `LegacyMapper`, pero NO se copiaron los outputs/resultados externos de pilotos anteriores.

Por tanto, antes de ejecutar cualquier corrección adicional (incluido `V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md`) se debe reconstruir una baseline local confiable de pruebas y outputs deterministas en este nuevo entorno.

Esta tarea es exclusivamente de REBASELINE / REPRODUCCIÓN / VALIDACIÓN DEL ENTORNO.

NO ejecutar R3A.
NO ejecutar R9.
NO declarar V4.3 cerrada.
NO modificar comportamiento funcional salvo que sea estrictamente necesario para corregir un problema de entorno reproducible y explícitamente autorizado.

---

# 1. Objetivo

Reconstruir y validar en el nuevo notebook:

1. el estado del repositorio LegacyMapper;
2. la configuración Git relevante;
3. el entorno Python;
4. la suite de tests;
5. los outputs deterministas mínimos necesarios para V4.3;
6. los índices reales sobre `C:\inetpub\wwwroot\2010\IST\Operacional`;
7. la herramienta diagnóstica R3;
8. una baseline limpia y reproducible antes de continuar con R3A.

El resultado debe permitir distinguir:

- fallos reales del producto;
- fallos de entorno;
- fallos causados por line endings/hash;
- outputs faltantes por cambio de PC;
- tests que dependen de artefactos externos no reconstruidos.

---

# 2. Inspección inicial obligatoria

Desde:

`C:\dev\LegacyMapper`

registrar:

```bat
git status
git branch --show-current
git rev-parse HEAD
git config --get core.autocrlf
python --version
python -m pip --version
```

También verificar:

```bat
where python
where git
where gh
```

Si existe:

```text
requirements-copilot.txt
```

registrar su contenido y NO instalar nada salvo que una prueba específica lo requiera.

No cambiar `core.autocrlf` todavía.

---

# 3. Inventario de artefactos presentes

Inventariar si existen localmente:

```text
output/
docs/V4_3/
prompts/V4_3/
tests/
tools/
PROJECT_STATE.json
```

y específicamente:

```text
tools/v4_3_ai_selection_diagnostic.py
tests/test_v4_3_final_ai_pilot_r3_proposal_diversity_diagnostic.py
prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md
```

Confirmar qué outputs históricos cerrados V4/V4.1/V4.2/V4.3 vienen versionados dentro del repo y cuáles eran externos/no versionados.

---

# 4. Baseline de tests — primera ejecución

Ejecutar SIN tocar archivos:

```bat
python -m unittest discover -s tests
```

Registrar:

```text
total
passed
failed
errors
skipped
```

Para cada failure/error:

- test exacto;
- archivo afectado;
- si compara hashes;
- si lee bytes crudos;
- si el archivo está marcado limpio por Git;
- si el contenido lógico coincide pero cambia CRLF/LF.

No corregir todavía.

---

# 5. Diagnóstico de line endings

Si reaparecen fallos de hash V4/V4.1, comprobar objetivamente:

```bat
git status --short
git config --get core.autocrlf
git ls-files --eol <archivo>
```

Para los archivos fallidos por hash, comparar:

- hash del worktree;
- hash del blob Git;
- EOL reportado por `git ls-files --eol`.

La tarea debe determinar si:

```text
FAIL = producto
```

o:

```text
FAIL = representación de worktree por autocrlf
```

No modificar hashes guardados ni outputs cerrados para “hacer pasar” tests.

Si existe una manera segura de recrear el worktree con LF sin cambiar contenido versionado ni contratos, documentarla como opción; NO aplicarla automáticamente salvo que sea necesaria para reconstruir una baseline válida y no altere el repositorio lógico.

---

# 6. Tests V4.3 específicos

Ejecutar por separado las suites relevantes de V4.3, incluyendo como mínimo las disponibles para:

- R2 hydration;
- R3 human documentation;
- R4 scaling;
- R5 AI context budgeting;
- R6 AI/consumer projection;
- R7 internal acceptance;
- R8 corrections;
- Copilot provider correction;
- proposal quality correction;
- R2 context budget correction;
- R3 proposal diversity diagnostic.

Registrar totales y verificar:

```text
0 failed
0 errors
```

para V4.3.

---

# 7. Reconstrucción de output determinista real

Crear una NUEVA salida local en el notebook, por ejemplo:

`C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline`

Si la carpeta existe y no está vacía, usar otra ruta nueva.

Ejecutar SOLO análisis determinista, sin IA real, usando el CLI vigente.

Preferencia:

```bat
python main.py full "C:\inetpub\wwwroot\2010\IST\Operacional" --output "C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline" --verbose
```

Si `full` intenta IA solo cuando se pasa `--allow-ai-interpretation`, entonces NO pasar esa flag.

No usar provider real.

Registrar:

- status;
- flow_count;
- path_count;
- outputs generados;
- tamaño total;
- stages.

Generar:

```bat
python main.py output-manifest "C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline"
```

---

# 8. Validación de índices reconstruidos

Verificar que existan y sean legibles los índices necesarios para el diagnóstico, por ejemplo:

```text
index/
ai_context/
documentation/
consumer_projection/
```

Comparar únicamente métricas estructurales conocidas, NO hashes contra outputs externos perdidos.

Referencias históricas útiles, solo como orientación:

```text
flow_count histórico: 12642
```

Si el nuevo conteo difiere:

- no asumir fallo;
- documentar la diferencia;
- comprobar si el árbol `C:\inetpub\wwwroot\2010\IST\Operacional` difiere de la copia anterior.

---

# 9. Ejecutar herramienta diagnóstica R3 sobre output reconstruido

Usar:

`tools/v4_3_ai_selection_diagnostic.py`

contra el nuevo output determinista.

NO invocar Copilot.

Registrar:

```text
selected candidates
rich bucket 0/1 candidates
final included records
rich final included records
rich excluded by budget
profile
package chars
payload estimated tokens
```

Verificar si la clasificación histórica:

```text
DIAGNOSIS_A_SELECTION_PACKING
```

sigue reproduciéndose en este notebook.

Verificar también:

`FLOW-0343552547`

si existe en los índices reconstruidos.

---

# 10. Revisar contradicción previa

La ronda anterior documentó simultáneamente:

```text
rich smallest excluded = 9680 chars
SMALL budget = 16000 chars
```

y también afirmó que:

```text
100% de rich candidates individualmente exceden el budget completo
```

Eso es inconsistente.

Esta ronda debe aclarar con datos reconstruidos:

- tamaño mínimo real de candidatos ricos;
- cuáles son `< 16000`;
- cuáles son `>= 16000`;
- por qué los candidatos ricos `< 16000` no entran al paquete final;
- cuánto budget ya estaba consumido cuando fueron considerados;
- orden exacto de evaluación.

NO corregir todavía el algoritmo.

Solo dejar la causa raíz precisa.

---

# 11. No ejecutar R3A todavía

El archivo:

`prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md`

queda congelado durante esta tarea.

No implementarlo.

Al final se decidirá si:

- puede ejecutarse tal cual;
- debe corregirse;
- debe reemplazarse por un R3A revisado.

---

# 12. Resultado esperado

Crear:

`docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md`

Debe incluir:

1. rutas vigentes;
2. commit/branch/status;
3. versión Python;
4. `core.autocrlf`;
5. baseline suite completa;
6. clasificación de fallos de hash/EOL;
7. tests V4.3;
8. output determinista reconstruido;
9. métricas principales;
10. diagnóstico R3 reproducido;
11. aclaración de la contradicción 9680 vs 16000;
12. estado de `FLOW-0343552547`;
13. archivos creados;
14. archivos modificados;
15. Runtime Independence;
16. conclusión sobre si R3A actual sigue siendo válido.

---

# 13. Estado final permitido

Si la baseline del nuevo notebook queda suficientemente confiable:

```text
V4_3_WORKSTATION_REBASELINE_READY
```

Si no:

```text
V4_3_WORKSTATION_REBASELINE_BLOCKED
```

---

# 14. Siguiente prompt

Solo si el diagnóstico queda claro:

- revisar `prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md`;
- si contiene premisas falsas/incompletas, crear:

`prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION_R1.md`

No ejecutar ese prompt en esta tarea.

---

# 15. Restricciones

NO:

- ejecutar Copilot real;
- ejecutar R9;
- declarar V4.3 cerrada;
- cambiar budgets;
- cambiar selector;
- cambiar hydration;
- cambiar prompts runtime de IA;
- cambiar provider;
- cambiar confidence;
- modificar outputs cerrados V4/V4.1 para satisfacer hashes;
- actualizar hashes grabados;
- tocar V5/Plugin Runtime.

Esta tarea es de reconstrucción y validación del entorno.

---

# 16. Formato final obligatorio

```text
STATUS:
<estado>

WORKSTATION:
<resumen>

GIT BASELINE:
<resumen>

PYTHON BASELINE:
<resumen>

FULL TEST SUITE:
<resultado>

EOL/HASH DIAGNOSIS:
<resultado>

V4.3 TESTS:
<resultado>

REBUILT DETERMINISTIC OUTPUT:
<ruta + métricas>

R3 DIAGNOSTIC REPRODUCED:
YES/NO

RICH FLOW SIZE FINDINGS:
<resumen>

FLOW-0343552547:
<resultado>

CURRENT R3A PROMPT:
VALID / NEEDS_REVISION / BLOCKED

FILES CREATED:
<lista>

FILES MODIFIED:
<lista>

RESULT DOCUMENT:
<ruta>

NEXT STEP:
<una sola acción>
```
