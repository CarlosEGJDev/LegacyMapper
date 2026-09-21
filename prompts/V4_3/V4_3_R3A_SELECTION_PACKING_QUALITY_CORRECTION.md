# PROMPT — V4.3 R3A — SELECTION/PACKING QUALITY CORRECTION

## 0. Contexto y estado

Repositorio LegacyMapper: `C:\dev\LegacyMapper`

Repositorio legacy real: `C:\inetpub\wwwroot\2010\IST\Operacional`

Estado vigente:
- V4.3 R0-R8 aprobados.
- R3 real (piloto): SUCCESS, 6 propuestas, pero concentradas en dead ends/unresolved/sin data operations.
- `docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md`: diagnóstico determinista,
  reproducido dos veces contra el repositorio real (12642 flows), clasificación `DIAGNOSIS_A_SELECTION_PACKING`.
- R9 NO debe ejecutarse. V4.3 NO debe declararse cerrada.

## 1. Causa raíz ya demostrada (no volver a diagnosticar, corregir)

`tools/v4_3_ai_selection_diagnostic.py` demostró, con datos reales del repositorio legacy real:

```text
candidatos seleccionados (select_flow_ids, SMALL, max_flows=80): 80
  de ellos, richness bucket 0/1 ("ricos"): 40
records incluidos en el paquete final: 6
  de ellos, richness bucket 0/1: 0        <- CERO records ricos llegan al request
records ricos EXCLUIDOS por budget: 40    <- el 100% de los candidatos ricos ofrecidos
candidato rico MÁS PEQUEÑO excluido: 9680 caracteres (> 60% del budget COMPLETO de SMALL=16000)
candidatos ricos más grandes: 84948-161040 caracteres (5-10x el budget COMPLETO de SMALL)
payload_estimated_tokens del request final: 4648 de un límite de 16000 (mucho margen sin usar)
```

El presupuesto de caracteres por perfil (`composer.PROFILES["SMALL"] = (80, 16000)`,
`["TINY"] = (20, 4000)`), reutilizado sin cambios por `ai_projection.ALLOWED_PROFILES`, es estructuralmente
incompatible con el tamaño real de un flow rico hidratado a esta escala (94-149 paths). La corrección
previa (V4.3 final AI pilot R2: "nunca abortar en el primer candidato sobredimensionado") es necesaria
pero insuficiente cuando el 100% de los candidatos ricos individualmente exceden el presupuesto total: no
hay "siguientes candidatos ricos que sí quepan".

## 2. Objetivo exacto

Corregir la calidad de selección/empaquetado para que un request `SMALL`/`TINY` real, sobre un repositorio
a esta escala, incluya al menos evidencia rica parcial (no cero) cuando existan candidatos ricos
disponibles, sin:

1. ampliar el presupuesto de caracteres/tokens del request final (eso ya tiene margen: 4648/16000 -- el
   problema no es el gate de `measure_request_payload`, es el presupuesto INTERNO de `package()`, ver
   sección 1);
2. inventar/truncar evidencia de un record incluido de forma que rompa trazabilidad
   (`evidence_refs`/`path_ids`/`terminal` deben sobrevivir íntegros si el record se incluye);
3. cambiar `confidence`, `terminal_type`, ni ninguna clasificación de riqueza existente
   (`_richness_bucket`/`_flow_richness_bucket`/`_record_richness_bucket`);
4. volver al comportamiento anterior donde flows triviales monopolizan la muestra (preservar diversidad).

No ampliar alcance a V5, Plugin Runtime, ni a agnosticismo de provider/tecnología.

## 3. Direcciones de diseño a evaluar (no prescriptivas, decidir con evidencia)

Explorar, con mediciones deterministas reales (no asumir cuál funciona):

- **Partición de un record rico** en sub-unidades citables dentro del mismo presupuesto (p. ej. un
  subconjunto de paths/terminales por record en vez de el flow completo), si y solo si ya existe o se
  puede definir un contrato de partición parcial explícito para `ai_projection` sin inventar semántica
  nueva de "evidencia incompleta pero no marcada como tal" -- cualquier partición debe declararse
  explícitamente truncada, nunca presentarse como completa.
- **Presupuesto diferenciado entre perfiles usados para selección de candidatos vs. empaquetado real**
  (el gate final de `measure_request_payload` ya tiene ~11000 tokens de margen sin usar en el caso
  demostrado -- investigar si ese margen puede trasladarse de forma determinista al presupuesto interno de
  `package()` sin violar el techo real del provider).
- **Priorizar records ricos "medianos"** (ni el más grande ni el más trivial) que sí quepan individualmente,
  en vez de round-robin puro por bucket -- medir si existen candidatos ricos de tamaño intermedio en el
  repositorio real que el orden actual nunca llega a intentar por agotarse el budget en candidatos más
  grandes o más pequeños antes.
- Cualquier otra dirección que preserve todos los invariantes de la sección 2 y se demuestre con
  fixtures/mediciones deterministas sobre el repositorio real, no solo sintéticas.

## 4. Principio obligatorio

Preservar: `Python selecciona y presupuesta; IA interpreta.` 100% determinista. Sin LLM, red, random ni
ranking IA para selección/budgeting.

## 5. No modificar

```text
CopilotProvider
SYSTEM_INSTRUCTION / USER_INSTRUCTION / FINDING_SCHEMA
measure_request_payload (el gate del request final, no el problema demostrado)
hydration.py (EvidenceHydrator.hydrate_flow, selección/deduplicación de paths)
consumer_projection.py
proposal_adapter.py
PROJECT_STATE.json
V5 / Plugin Runtime
distribution builder / requirements-copilot.txt
```

Si la corrección mínima necesaria requiere tocar `composer.PROFILES` (compartido con paquetes no-AI),
evaluar primero si `ai_projection` puede definir su propio presupuesto interno sin modificar
`composer.PROFILES` para otros consumidores -- documentar la decisión explícitamente si se toca.

## 6. Tests obligatorios (mínimo)

1. Repetir, como regresión, el escenario real demostrado en el diagnóstico (fixture sintética equivalente
   a "40 candidatos ricos, todos > budget individual; 40 candidatos triviales, todos dentro de budget"):
   verificar que la corrección SÍ incluye al menos un record rico (parcial o completo, según diseño
   elegido) en el paquete final, sin exceder el presupuesto del request final.
2. Ningún record incluido pierde `evidence_refs`/`path_ids`/`terminal` de forma no declarada.
3. Diversidad preservada: no volver a 100% trivial cuando existan candidatos ricos.
4. `measure_request_payload` del request final sigue dentro del límite real del provider.
5. Sin mutación de `confidence`/`terminal_type`/clasificación de riqueza existente.
6. Determinismo: misma entrada, misma salida, mismo orden.
7. Sin llamada a provider/red en ningún test.
8. Regresión completa V4.2/V4.3 (R2, R5, R6, R7, R8, diversidad, budget, y el nuevo diagnóstico R3) en
   verde.

## 7. Suite

Ejecutar `python -m unittest discover -s tests`. Criterio: `0 failed`, `0 errors` en todo lo perteneciente
a V4.2/V4.3 y a esta corrección (los fallos preexistentes de hash de baseline V4/V4.1 documentados en
`docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md` sección 12, si siguen
reproduciéndose por el mismo motivo de entorno ya documentado, deben reportarse explícitamente, no
ocultarse ni "arreglarse" tocando artefactos de baseline cerrados fuera de alcance).

## 8. Documento de resultado

Crear: `docs/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md`. Debe incluir: evidencia del
diagnóstico R3 (causa raíz), diseño evaluado y elegido, por qué se descartaron las alternativas, algoritmo
nuevo exacto, invariantes preservados (evidencia atómica, diversidad, determinismo, sin mutación de
confidence), tests, resultados de suite completa, Runtime Independence, restricciones, y estado final.

## 9. Estado final permitido

Si pasa: `V4_3_READY_FOR_R3_RERUN` (habilita, en una tarea FUTURA separada, un nuevo piloto real con la
corrección aplicada -- no ejecutar ese rerun en esta tarea).

Si no: `V4_3_SELECTION_PACKING_CORRECTION_BLOCKED`.

NO usar `V4_3_CLOSED`. NO ejecutar R9.

## 10. Formato final obligatorio

```text
STATUS:
<estado>

ROOT CAUSE (heredada del diagnóstico R3):
<resumen>

DESIGN EVALUATED:
<resumen>

DESIGN CHOSEN:
<resumen>

FILES MODIFIED:
<lista>

ATOMIC EVIDENCE:
<resultado>

DIVERSITY PRESERVED:
<resultado>

TESTS:
<resultado>

RUNTIME INDEPENDENCE:
PASS/FAIL

RESTRICTIONS:
PASS/FAIL

RESULT DOCUMENT:
<ruta>

NEXT STEP:
<una sola acción>
```

Realizar únicamente esta corrección. NO ejecutar piloto real. NO ejecutar R9.
