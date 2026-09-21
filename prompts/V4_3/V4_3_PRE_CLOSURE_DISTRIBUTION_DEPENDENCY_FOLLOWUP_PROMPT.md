# PROMPT — V4.3 PRE-CLOSURE DISTRIBUTION DEPENDENCY FOLLOW-UP

## Contexto

Repositorio:

`E:\IAProyectos\LegacyMapper`

La corrección pre-cierre del provider COPILOT ya fue implementada y validada.

Estado actual documentado:

`V4_3_READY_FOR_FINAL_AI_PILOT`

Ya existe en la raíz del repositorio:

`requirements-copilot.txt`

con:

```text
github-copilot-sdk>=1.0.14
```

La dependencia es opcional y corresponde únicamente al provider real COPILOT.

La suite posterior a la corrección terminó con:

```text
2096 tests
0 failures
0 errors
132 skips
```

R9 NO debe ejecutarse.

V4.3 NO debe declararse cerrada.

---

# Hallazgo de revisión

El piloto externo real se ejecuta desde una distribución limpia creada mediante:

`tools/v4_3_r7_build_pilot_distribution.py`

Se verificó manualmente:

```bat
findstr /N /I "requirements requirements-copilot" tools\v4_3_r7_build_pilot_distribution.py
```

Resultado:

```text
<sin resultados>
```

Por lo tanto, el distribution builder actual no referencia ni copia:

`requirements-copilot.txt`

Esto crea una inconsistencia:

- el repositorio declara correctamente la dependencia opcional;
- pero la distribución limpia usada para el piloto puede no transportar esa declaración;
- el piloto no debe depender accidentalmente de que el SDK ya esté instalado en el Python global del equipo.

---

# Objetivo exacto

Realizar únicamente un micro-ajuste pre-piloto para que la distribución limpia de V4.3 incluya:

`requirements-copilot.txt`

junto a los artefactos runtime ya permitidos.

No realizar ningún otro cambio funcional.

---

# Cambio requerido

Revisar:

`tools/v4_3_r7_build_pilot_distribution.py`

y agregar `requirements-copilot.txt` al allowlist/copia de distribución usando el mecanismo ya existente.

La distribución resultante debe contener, en su raíz:

```text
main.py
requirements-copilot.txt
legacy_documenter/
...
```

No crear un nuevo sistema de distribución.

No instalar dependencias desde el builder.

No ejecutar `pip`.

No autenticar GitHub desde el builder.

No descargar runtime de Copilot SDK desde el builder.

El builder solamente debe transportar la declaración de dependencia opcional.

---

# Restricciones

NO modificar:

```text
legacy_documenter/llm/providers/copilot.py
consumer_projection
hydration
selection
human documentation
flow confidence
terminal resolution
R8 presentation logic
ProviderRegistry
V5
Plugin Runtime
PROJECT_STATE.json
```

salvo documentación específica de este follow-up si es necesaria.

NO ejecutar R9.

NO ejecutar el piloto final real.

NO cambiar `requirements-copilot.txt`, salvo que exista una razón técnica imprescindible; si no existe, dejarlo exactamente como está.

NO convertir `github-copilot-sdk` en dependencia obligatoria del runtime determinista.

NO incorporar Copilot real a tests.

---

# Tests requeridos

Agregar o ajustar únicamente los tests necesarios para verificar que el distribution builder:

1. incluye `requirements-copilot.txt`;
2. conserva `main.py`;
3. conserva el allowlist runtime existente;
4. no copia `docs/`, `prompts/`, `tests/`, `PROJECT_STATE.json` ni otros artefactos de desarrollo no permitidos;
5. sigue rechazando destino no vacío si esa es la semántica existente;
6. mantiene comportamiento previo salvo por la incorporación explícita de `requirements-copilot.txt`.

Usar fixtures/directorios temporales.

No ejecutar Copilot real.

Después ejecutar:

```text
tests específicos del builder/distribución
suite completa
```

Criterio obligatorio:

```text
0 failures
0 errors
```

---

# Verificación manual requerida

Construir una distribución de prueba en un directorio temporal o de test, NO en el directorio del piloto final del usuario.

Verificar que exista:

```text
<distribution-root>\requirements-copilot.txt
```

y que su contenido incluya:

```text
github-copilot-sdk>=1.0.14
```

Verificar también que el runtime siga sin contener dependencias hacia:

```text
docs/
prompts/
governance/
results/
PROJECT_STATE
tests/
```

La presencia de `requirements-copilot.txt` en la raíz de la distribución es válida: es una declaración de dependencia runtime opcional, no una dependencia hacia documentación/desarrollo.

---

# Documentación

Actualizar:

`docs/V4_3/V4_3_PRE_CLOSURE_COPILOT_PROVIDER_CORRECTION_RESULT.md`

solo si el repositorio usa ese documento como resultado acumulativo de la corrección.

En caso contrario crear:

`docs/V4_3/V4_3_PRE_CLOSURE_DISTRIBUTION_DEPENDENCY_FOLLOWUP_RESULT.md`

Preferir el enfoque que siga la convención existente del repositorio.

Documentar:

- hallazgo;
- archivo modificado;
- motivo;
- tests;
- comprobación de distribución;
- Runtime Independence;
- restricciones;
- estado final.

Actualizar también:

`docs/V4_3/V4_3_FINAL_AI_PILOT_INSTRUCTIONS.md`

para que las instrucciones del piloto final indiquen explícitamente:

1. construir una distribución limpia usando el builder actualizado;
2. entrar a esa distribución;
3. instalar la dependencia opcional desde ESA distribución:

```bat
python -m pip install -r requirements-copilot.txt
```

4. verificar autenticación:

```bat
gh auth status
```

5. solo entonces ejecutar el `full`.

No asumir que el SDK está instalado previamente en el entorno.

---

# Estado final permitido

Si todo pasa:

```text
V4_3_READY_FOR_FINAL_AI_PILOT
```

Si falla:

```text
V4_3_PRE_CLOSURE_CORRECTION_BLOCKED
```

NO usar:

```text
V4_3_CLOSED
```

---

# Formato obligatorio de respuesta

```text
STATUS:
<estado>

FILES MODIFIED:
<lista>

DISTRIBUTION BUILDER:
<resumen>

REQUIREMENTS-COPILOT IN DISTRIBUTION:
PASS/FAIL

TESTS:
<resultado>

RUNTIME INDEPENDENCE:
PASS/FAIL

RESTRICTIONS:
PASS/FAIL

RESULT DOCUMENT:
<ruta>

FINAL PILOT INSTRUCTIONS:
<ruta>

NEXT STEP:
<una sola acción>
```

Realizar el micro-ajuste, tests y documentación.

NO ejecutar el piloto final.
NO ejecutar R9.
