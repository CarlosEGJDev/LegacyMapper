# V4.3 — Instrucciones para el rerun del piloto final de IA

Este documento describe cómo repetir el piloto final real de IA **después**
de la corrección de calidad de selección de candidatos documentada en
`docs/V4_3/V4_3_FINAL_AI_PILOT_PROPOSAL_QUALITY_CORRECTION_RESULT.md`. El
rerun en sí **no** se ejecuta como parte de esa corrección — este documento
solo deja instrucciones para cuando se decida ejecutarlo.

No ejecutar R9 como parte de este rerun. No declarar V4.3 cerrada a partir de
este rerun.

---

## 1. Precondición

- `docs/V4_3/V4_3_FINAL_AI_PILOT_PROPOSAL_QUALITY_CORRECTION_RESULT.md` debe
  indicar `V4_3_READY_FOR_FINAL_AI_PILOT_RERUN`. Si indica
  `V4_3_PROPOSAL_QUALITY_CORRECTION_BLOCKED`, no ejecutar este rerun todavía.
- Repositorio legacy de referencia (solo lectura):
  `C:\Users\cgalianj\source\IST_40\operacional`.

## 2. Salida en una ubicación NUEVA

No reutilizar la salida del piloto final anterior. Usar, por ejemplo:

```text
E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final_r2
```

## 3. Comando

Igual que el piloto final original, con `--allow-ai-interpretation` y el
proveedor real ya configurado (Copilot):

```text
python main.py "C:\Users\cgalianj\source\IST_40\operacional" --output "E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final_r2" --verbose --allow-ai-interpretation
```

No usar `python -m tools.manual_verify_full_pipeline` para este rerun: esa
herramienta inyecta siempre `FakeLLMProvider` y nunca llama al proveedor real
(ver `AGENTS.md`, sección "Manual AI-Path Verification") — es exclusivamente
para verificación manual sin llamada real, no para el piloto.

## 4. Qué revisar en la salida del rerun

En el directorio de salida:

- `RUN_SUMMARY.json` / `RUN_SUMMARY.md` — confirmar
  `AI_INTERPRETATION: SUCCESS`, `PROPOSAL_GENERATION: SUCCESS`,
  `canonical knowledge produced: False`,
  `Technical Lead approval: False` (sin cambios de contrato).
- `AI_PROPOSALS.json` / `AI_PROPOSALS_PENDING_REVIEW.md`:
  - **Cantidad de propuestas**: registrar el número; no se impuso un tope
    determinista de propuestas en esta corrección (ver sección 15 del
    documento de resultado) — sigue siendo cuántos `findings` devuelva el
    modelo, pero ahora sobre una muestra de flows más diversa.
  - **Diversidad de evidencia**: verificar que no todas las propuestas sigan
    el patrón `"has no recorded data operations and ends at an unresolved
    node"`. Se espera ver, cuando el repositorio los tenga disponibles,
    algunos hallazgos sobre flows con stored procedures, transacciones o
    escrituras confirmadas.
  - **Idioma**: seguirá en inglés (deuda documentada, no corregida en esta
    ronda) — no es una regresión si aparece en inglés.
  - **Confidence/rationale**: el campo `confidence` de cada rationale
    (`"AI-proposed interpretation (confidence: ...)"`) es la confianza que el
    LLM declara sobre su propia observación, no la `confidence` de evidencia
    del flow — ver sección 8 del documento de resultado antes de interpretar
    este campo como si midiera la solidez de la evidencia del flow.
  - **Provider/modelo**: confirmar que el proveedor y modelo real registrados
    coinciden con la configuración vigente (el piloto anterior registró
    `gpt-5.6-luna`; si cambia, documentarlo, pero esta corrección no cambió
    el modelo configurado).
  - **Ausencia de secretos**: revisar que no aparezcan credenciales, tokens ni
    cadenas de conexión en las propuestas o en la evidencia citada.
- `PROJECT_STATE.json`: confirmar que `ai_knowledge_generated` y
  `provider_calls`/`real_llm_calls` reflejan el rerun solo si así lo decide
  explícitamente un paso posterior — esta corrección no escribe en
  `PROJECT_STATE.json`, y el rerun tampoco debe hacerlo por sí solo sin una
  decisión explícita de actualización de estado.
- Confirmar que `canonical knowledge produced` sigue en `False` y
  `Technical Lead approval` sigue en `False` — el rerun no aprueba ni
  promueve nada por sí mismo.

## 5. Después del rerun

No ejecutar R9 automáticamente. No declarar `V4_3_CLOSED`. Reportar los
hallazgos del rerun (cantidad de propuestas, diversidad observada, y
cualquier desviación de lo esperado en esta lista) como su propio resultado,
separado de este documento de instrucciones.
