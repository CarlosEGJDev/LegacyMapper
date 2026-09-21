# PROMPT — V4.3 PRE-CLOSURE COPILOT PROVIDER CORRECTION

## 0. Autoridad, alcance y estado

Repositorio de trabajo:

`E:\IAProyectos\LegacyMapper`

Estado vigente:

- V4.3 R0–R8 ejecutados y aprobados.
- R8 aprobado.
- R9 NO debe ejecutarse todavía.
- Esta tarea existe únicamente para corregir problemas descubiertos en el piloto real de GitHub Copilot SDK antes del cierre formal.
- No ampliar alcance funcional.
- No iniciar V5.
- No introducir Plugin Runtime.
- No modificar `consumer_projection`.
- No modificar semántica de selección, hidratación, documentación humana, confianza de flows ni resolución de terminales.
- No declarar V4.3 cerrada.

Principio permanente:

> Runtime Independence / Distribution Boundary

El runtime/producto no puede depender de:

- `docs/`
- `prompts/`
- `governance/`
- `results/`
- `PROJECT_STATE`
- `tests/`
- artefactos de desarrollo

---

# 1. Evidencia empírica del piloto real

## 1.1 Dependencia Python ausente

Durante el primer piloto real, el provider COPILOT falló porque el SDK no estaba instalado.

Error observado:

```text
ModuleNotFoundError: No module named 'copilot'
```

El provider ejecuta:

```python
from copilot import CopilotClient
```

La dependencia que se instaló y validó correctamente fue:

```text
github-copilot-sdk==1.0.14
```

Import verificado:

```text
C:\Users\akio-\AppData\Local\Programs\Python\Python314\Lib\site-packages\copilot\__init__.py
```

No asumir automáticamente que debe fijarse exactamente `1.0.14`.

Primero inspeccionar cómo LegacyMapper declara dependencias y respetar su convención actual.

Si existe separación entre dependencias base y dependencias opcionales/provider-specific, preservar ese diseño.

No convertir Copilot en requisito global si actualmente el provider COPILOT es opcional.

---

## 1.2 Autenticación ausente

Una vez instalado el SDK, se obtuvo:

```text
JsonRpcError:
Request models.list failed with message:
Not authenticated. Please authenticate first.
```

El entorno fue corregido instalando GitHub CLI y autenticando:

```text
gh auth login
```

Después de eso:

```text
client.start()    OK
list_models()     OK
```

Modelo lógico ofrecido por el SDK:

```text
id=auto
name=Auto
```

Modelo real finalmente usado:

```text
gpt-5.6-luna
```

NO implementar autenticación nueva dentro de LegacyMapper.

La autenticación sigue siendo responsabilidad del entorno externo.

Sí debe mejorarse el diagnóstico del provider para que este tipo de error no quede oculto.

---

## 1.3 Runtime local del SDK inicialmente defectuoso

Durante las pruebas se detectó también un problema del runtime local descargado por GitHub Copilot SDK.

Error real:

```text
PermissionError: [WinError 5] Acceso denegado
```

ocurrido durante la preparación del runtime local bajo:

```text
C:\Users\akio-\AppData\Local\github-copilot-sdk\cli\1.0.85\prebuilds
```

El runtime se reparó externamente y posteriormente funcionó.

Esto NO requiere que LegacyMapper gestione, repare o manipule la caché/runtime interno del SDK.

Sí demuestra que el provider debe preservar suficiente diagnóstico seguro para identificar:

- fase del fallo;
- tipo de excepción;
- modelo intentado, cuando exista.

---

## 1.4 Error demasiado genérico de CopilotProvider

El provider actual termina encapsulando fallos diferentes como:

```text
PROVIDER_ERROR
Copilot provider request failed
```

Esto ocultó causas reales como:

```text
ModuleNotFoundError
JsonRpcError / Not authenticated
PermissionError
```

Además, cuando `config.model_id` estaba vacío y el provider descubría dinámicamente el modelo lógico:

```text
auto
```

un error posterior seguía reportando:

```text
model_id=""
```

por lo que se perdía el modelo realmente intentado.

---

# 2. Validación real posterior — comportamiento correcto confirmado

Después de corregir únicamente el entorno, el SDK fue probado directamente con éxito:

```text
CopilotClient                 OK
client.start()                OK
list_models()                 OK
create_session()              OK
send_and_wait()               OK
logical model                 auto
actual model                  gpt-5.6-luna
```

Después se probó `CopilotProvider` directamente con structured output:

```text
STATUS:
SUCCESS

MODEL:
gpt-5.6-luna

SCHEMA STATUS:
VALID_STRUCTURED_OUTPUT

VALIDATION ERRORS:
[]

ERROR:
None
```

Finalmente se validó un flow REAL del sistema:

```text
FLOW-0343552547
```

Payload medido:

```text
payload_bytes:              111886
payload_characters:         111875
payload_estimated_tokens:   27969
```

Resultado:

```text
STATUS:
SUCCESS

MODEL:
gpt-5.6-luna

SCHEMA STATUS:
VALID_STRUCTURED_OUTPUT

VALIDATION ERRORS:
[]

ERROR:
None
```

La IA identificó correctamente:

```text
Load -> Page_Load
CobLiquidacionDeudaPrev.ascx
EP-0494012737
FLOW-0343552547
```

y procedimientos confirmados como:

```text
PCOB_DEUDAS_ENCABEZADO.OBTENERGASTOSCOBEJ
PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV
PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV2
PCOB_FACTORES.OBTENERVALORES
```

También mantuvo correctamente incertidumbres, por ejemplo:

- no afirmó orden exacto de todas las rutas;
- no inventó qué devuelven los SP;
- no convirtió `BeginTrans` en evidencia de escritura;
- mantuvo el flow global como `unresolved`.

Conclusión obligatoria para esta tarea:

- NO modificar selección/hidratación/proyección.
- NO modificar `consumer_projection`.
- NO modificar structured output contract funcional.
- NO optimizar todavía el contexto de ~28K tokens.
- El tamaño del payload NO está demostrado como defecto.
- El provider funcionalmente puede trabajar con el payload real.

---

# 3. Objetivo exacto

Implementar una corrección mínima pre-cierre para:

1. declarar correctamente la dependencia runtime de GitHub Copilot SDK;
2. mejorar el diagnóstico seguro de `CopilotProvider`;
3. preservar el modelo intentado cuando se selecciona dinámicamente;
4. agregar tests unitarios/regresión;
5. mantener intacto el comportamiento funcional ya validado.

No realizar cambios fuera de este alcance.

---

# 4. Dependencia runtime

Inspeccionar primero el mecanismo actual de dependencias del repositorio.

Agregar:

```text
github-copilot-sdk
```

según la convención existente.

Reglas:

- no crear un sistema de packaging nuevo;
- no duplicar dependencias;
- no agregar dependencias innecesarias;
- no hacer obligatoria globalmente la dependencia si el diseño actual permite providers opcionales;
- preservar funcionamiento determinista sin Copilot;
- preservar FAKE provider;
- preservar registry actual.

La distribución que habilite COPILOT debe poder ejecutar:

```python
from copilot import CopilotClient
```

sin depender de que el entorno de desarrollo tenga el paquete instalado manualmente.

---

# 5. CopilotProvider — diagnóstico por fase

Revisar la implementación real de `CopilotProvider`.

La secuencia actual conceptualmente es:

```text
CopilotClient
    ↓
client.start()
    ↓
list_models()
    ↓
create_session()
    ↓
send_and_wait()
    ↓
structured parse
```

Cuando exista un error, debe poder determinarse en qué fase ocurrió.

Usar identificadores estables equivalentes a:

```text
client_init
client_start
list_models
create_session
send_and_wait
structured_parse
```

No es obligatorio utilizar exactamente esos nombres si el repositorio ya tiene una convención mejor.

No crear una jerarquía nueva de excepciones.

Usar `ProviderError` existente.

---

# 6. ProviderError.details

Aprovechar el mecanismo existente:

```python
ProviderError.details
```

Los errores deberían preservar, cuando sea posible:

```json
{
  "phase": "list_models",
  "exception_type": "JsonRpcError",
  "attempted_model": "auto"
}
```

Opcionalmente, si puede hacerse de forma segura:

```json
{
  "sanitized_message": "Not authenticated. Please authenticate first."
}
```

No copiar indiscriminadamente `repr(exc)` ni contenido completo de excepciones a artefactos persistentes.

---

# 7. Sanitización obligatoria

Nunca exponer en:

- `ProviderError.details`
- `RUN_SUMMARY`
- logs públicos
- resultados serializados
- artefactos persistentes

información como:

```text
GitHub tokens
GH_TOKEN
GITHUB_TOKEN
COPILOT_GITHUB_TOKEN
Authorization headers
cookies
credential material
OAuth secrets
session tokens
API keys
```

Si una excepción contiene material potencialmente sensible, aplicar sanitización conservadora.

Preferir conservar:

```text
phase
exception_type
attempted_model
sanitized_message
```

sin secretos.

---

# 8. attempted_model

Caso real:

```text
config.model_id = ""
```

Luego:

```text
list_models() -> auto
```

Después de seleccionar `auto`, si falla una fase posterior, el error debe conservar:

```text
attempted_model = "auto"
```

o equivalente.

No volver a perder el modelo usando solamente:

```text
model_id=""
```

En caso de éxito, preservar comportamiento actual:

```text
response.model_id = modelo real devuelto por SDK
```

Por ejemplo:

```text
gpt-5.6-luna
```

No modificar esa semántica.

---

# 9. Taxonomía de errores

No rediseñar toda la taxonomía.

Preservar conceptos actuales como:

```text
PROVIDER_ERROR
MODEL_UNAVAILABLE
TIMEOUT
INVALID_STRUCTURED_OUTPUT
```

Es aceptable que un error de autenticación continúe siendo:

```text
PROVIDER_ERROR
```

si `details` contiene diagnóstico suficiente.

No introducir una taxonomía nueva amplia en esta tarea.

---

# 10. Timeout

Revisar el tratamiento actual de timeout.

Si actualmente existe algo equivalente a:

```python
except TimeoutError:
```

no ampliar arbitrariamente el catch.

Si el SDK usa otro tipo específico y hay evidencia concreta en el código o tests, documentarlo.

Modificar solo si está demostrado.

No especular.

---

# 11. Structured output

NO cambiar la semántica funcional ya validada.

Debe seguir funcionando:

```text
send_and_wait
    ↓
content
    ↓
json.loads
    ↓
validación existente
```

El resultado real ya validado fue:

```text
SCHEMA STATUS:
VALID_STRUCTURED_OUTPUT
```

y debe conservarse.

---

# 12. Tests requeridos

Agregar tests unitarios sin llamadas reales a GitHub/Copilot.

## T1 — provider/import

Validar según el patrón existente que el provider puede utilizar el SDK cuando está disponible.

No hacer conexión real.

## T2 — error en client initialization

Simular fallo en:

```python
CopilotClient(...)
```

Verificar:

```text
error/status compatible
details.phase correcto
details.exception_type correcto
sin secretos
```

## T3 — error en client.start

Simular:

```python
await client.start()
```

fallando.

Verificar diagnóstico.

## T4 — error en list_models

Simular un error semejante a:

```text
Not authenticated. Please authenticate first.
```

Validar:

```text
phase = list_models
exception_type preservado
mensaje sanitizado si corresponde
```

## T5 — modelo dinámico preservado

Usar:

```text
config.model_id=""
```

Mock:

```text
list_models() -> auto
```

Provocar después fallo en:

```text
create_session
```

o:

```text
send_and_wait
```

Verificar:

```text
attempted_model = auto
```

## T6 — create_session

Simular fallo en `create_session`.

Validar fase correcta.

## T7 — send_and_wait

Simular fallo en `send_and_wait`.

Validar fase correcta.

## T8 — éxito existente

Preservar un test exitoso con:

```text
SUCCESS
structured output válido
actual model preservado
```

## T9 — sanitización

Crear excepción sintética que incluya por ejemplo:

```text
Authorization: Bearer SECRET_TOKEN
```

o:

```text
GH_TOKEN=SECRET
```

Verificar que `SECRET_TOKEN` / `SECRET` no aparece en:

```text
ProviderError.details
message
serialized result
```

No usar secretos reales.

---

# 13. Regresión

Ejecutar:

1. tests específicos de `CopilotProvider`;
2. tests relevantes de LLM/projection;
3. suite completa.

Baseline previo:

```text
2087 tests
0 failures
0 errors
132 skips
```

Como se agregarán tests, el total puede aumentar.

Criterio obligatorio:

```text
0 failures
0 errors
```

Documentar:

```text
total
passed
failed
errors
skipped
```

---

# 14. Restricciones estrictas

NO modificar funcionalmente:

```text
consumer_projection
hydration semantics
selection semantics
human documentation semantics
flow confidence
terminal resolution
R8 presentation logic
V5
Plugin Runtime
technology detection
provider abstraction redesign
generic provider architecture
PROJECT_STATE
```

No ejecutar R9.

No declarar V4.3 cerrada.

No crear features nuevas.

No cambiar comportamiento determinista.

No utilizar Copilot real en tests.

No incorporar outputs del piloto real como fixtures.

Usar mocks/fixtures sintéticas.

---

# 15. Runtime Independence / Distribution Boundary

Comprobar explícitamente que runtime/product code no dependa de:

```text
docs/
prompts/
governance/
results/
PROJECT_STATE
tests/
```

La dependencia ejecutable `github-copilot-sdk` sí puede pertenecer al provider COPILOT.

No crear dependencia runtime hacia documentación o estado de desarrollo.

---

# 16. Compatibilidad obligatoria

Preservar:

- provider id actual;
- registry actual;
- FAKE provider;
- COPILOT provider;
- API pública actual;
- contratos actuales;
- status actuales;
- structured output actual;
- CLI actual;
- funcionamiento determinista sin IA;
- funcionamiento cuando COPILOT no se solicita.

---

# 17. Documento de resultado

Crear:

```text
docs/V4_3/V4_3_PRE_CLOSURE_COPILOT_PROVIDER_CORRECTION_RESULT.md
```

Debe incluir:

1. objetivo;
2. causas raíz observadas;
3. archivos modificados;
4. dependencia agregada;
5. cambios diagnósticos;
6. fases diagnósticas soportadas;
7. sanitización;
8. manejo de `attempted_model`;
9. tests agregados;
10. resultados de tests;
11. Runtime Independence;
12. restricciones verificadas;
13. deuda residual;
14. estado final.

Estado final permitido si todo pasa:

```text
V4_3_READY_FOR_FINAL_AI_PILOT
```

Si falla aceptación:

```text
V4_3_PRE_CLOSURE_CORRECTION_BLOCKED
```

NO usar:

```text
V4_3_CLOSED
```

---

# 18. Instrucciones del piloto final

Crear también:

```text
docs/V4_3/V4_3_FINAL_AI_PILOT_INSTRUCTIONS.md
```

Debe contener las instrucciones para el piloto externo final.

Comando previsto:

```bat
python main.py full "E:\IAProyectos\revision\revision-main" --output "E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final" --allow-ai-interpretation --verbose
```

Después:

```bat
python main.py output-manifest "E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final"
```

NO ejecutar el piloto dentro de esta tarea.

Las instrucciones deben pedir comprobar como mínimo:

```text
RUN_SUMMARY.json
RUN_SUMMARY.md
OUTPUT_MANIFEST
AI_INTERPRETATION status
provider_id
model_id
proposal_count
AI proposal artifacts
human documentation
consumer projection
```

Si ocurre error, verificar que incluya diagnóstico suficiente sin exponer secretos.

---

# 19. Orden obligatorio de trabajo

Ejecutar exactamente en este orden:

1. leer implementación actual;
2. identificar mecanismo de dependencias;
3. identificar tests existentes;
4. determinar cambio mínimo;
5. modificar dependencia;
6. modificar `CopilotProvider`;
7. agregar tests;
8. ejecutar tests específicos;
9. ejecutar tests relevantes;
10. ejecutar suite completa;
11. comprobar Runtime Independence;
12. comprobar restricciones;
13. crear documento de resultado;
14. crear instrucciones del piloto final.

No modificar código antes de entender la implementación existente.

---

# 20. Criterios de aceptación

La tarea se acepta únicamente si:

```text
A. github-copilot-sdk queda declarado correctamente según la arquitectura existente.

B. CopilotProvider mantiene su comportamiento funcional exitoso.

C. Los errores conservan al menos:
   - phase
   - exception_type
   - attempted_model cuando exista

D. No se filtran secretos.

E. El modelo dinámico "auto" no se pierde en errores posteriores.

F. Structured output válido sigue funcionando.

G. Tests no realizan llamadas reales a Copilot.

H. Suite completa termina con 0 failures y 0 errors.

I. Runtime Independence se preserva.

J. No se modifica V5.

K. No se modifica Plugin Runtime.

L. No se modifica consumer_projection.

M. No se ejecuta R9.

N. Estado final:
   V4_3_READY_FOR_FINAL_AI_PILOT
   o
   V4_3_PRE_CLOSURE_CORRECTION_BLOCKED
```

---

# 21. Formato obligatorio de la respuesta final

Responder exactamente con esta estructura:

```text
STATUS:
<estado>

FILES MODIFIED:
<lista>

DEPENDENCY:
<resultado>

COPILOT DIAGNOSTICS:
<resumen>

SANITIZATION:
<resumen>

ATTEMPTED MODEL:
<resumen>

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

No responder solo con explicación general.

Realizar implementación, tests y documentación.

NO ejecutar R9.
NO ejecutar el piloto externo final.
