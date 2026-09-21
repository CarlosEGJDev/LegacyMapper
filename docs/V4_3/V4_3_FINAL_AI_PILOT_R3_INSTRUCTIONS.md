# V4.3 — Instrucciones para el piloto final de IA, rerun R3

Este documento describe cómo repetir el piloto final real de IA **después**
de la corrección de regresión de budget de contexto documentada en
`docs/V4_3/V4_3_FINAL_AI_PILOT_R2_CONTEXT_BUDGET_CORRECTION_RESULT.md` (que a
su vez sigue a la corrección de diversidad de propuestas de
`docs/V4_3/V4_3_FINAL_AI_PILOT_PROPOSAL_QUALITY_CORRECTION_RESULT.md`). El
rerun R3 en sí **no** se ejecuta como parte de esta corrección — este
documento solo deja instrucciones para cuando se decida ejecutarlo.

No ejecutar R9 como parte de este rerun. No declarar V4.3 cerrada a partir de
este rerun.

---

## 1. Precondición

- `docs/V4_3/V4_3_FINAL_AI_PILOT_R2_CONTEXT_BUDGET_CORRECTION_RESULT.md` debe
  indicar `V4_3_READY_FOR_FINAL_AI_PILOT_R3`. Si indica
  `V4_3_CONTEXT_BUDGET_CORRECTION_BLOCKED`, no ejecutar este rerun todavía.
- Reconstruir la distribución limpia **después** de esta corrección (la
  corrección de budget tocó `legacy_documenter/context/ai_projection.py`, que
  forma parte del runtime empaquetado). Seguir el mismo procedimiento de
  distribución limpia ya validado en
  `docs/V4_3/V4_3_PRE_CLOSURE_DISTRIBUTION_DEPENDENCY_FOLLOWUP_RESULT.md`
  antes de ejecutar el rerun contra la distribución (no contra el checkout de
  desarrollo) si ese es el modo de ejecución elegido para R3.

## 2. Repositorio real y salida en una ubicación NUEVA

Repositorio real a analizar en este rerun:

```text
E:\IAProyectos\revision\revision-main
```

No reutilizar la salida de los reruns anteriores. Usar, por ejemplo:

```text
E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final_r3
```

## 3. Comando

Subcomando correcto (`full`, no el atajo legado de un solo argumento), con
`--allow-ai-interpretation` para habilitar la pasada de IA opcional:

```text
python main.py full "E:\IAProyectos\revision\revision-main" --output "E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final_r3" --verbose --allow-ai-interpretation
```

No usar `python -m tools.manual_verify_full_pipeline` para este rerun: esa
herramienta inyecta siempre `FakeLLMProvider` y nunca llama al proveedor
real (ver `AGENTS.md`, sección "Manual AI-Path Verification") — es
exclusivamente para verificación manual sin llamada real, no para el piloto.

## 4. Qué revisar en la salida del rerun

En el directorio de salida:

- `RUN_SUMMARY.json` / `RUN_SUMMARY.md`:
  - Confirmar que ninguna etapa reporta `CONTEXT_TOO_LARGE` salvo que
    realmente no exista ninguna combinación de flows que quepa en `SMALL` ni
    en `TINY` (fail-closed legítimo, no la regresión corregida en esta
    ronda).
  - Confirmar `ai_invoked: true` si `AI_INTERPRETATION` fue intentada y no
    fue rechazada por presupuesto — si vuelve a aparecer
    `ai_invoked: false` con `CONTEXT_TOO_LARGE`, la corrección de esta ronda
    no resolvió el caso real y debe tratarse como hallazgo, no como éxito.
  - `canonical knowledge produced: False` y
    `Technical Lead approval: False` deben seguir sin cambios de contrato.
- `AI_PROPOSALS.json` / `AI_PROPOSALS_PENDING_REVIEW.md` (si
  `PROPOSAL_GENERATION` corrió):
  - **Diversidad de evidencia**: verificar que la corrección de diversidad de
    la ronda anterior sigue vigente (no solo "no falla por presupuesto", sino
    que las propuestas no vuelven a ser homogéneas — ver
    `docs/V4_3/V4_3_FINAL_AI_PILOT_PROPOSAL_QUALITY_CORRECTION_RESULT.md`
    secciones 6-7 para el criterio).
  - **Cantidad de propuestas**: registrar el número; sigue sin existir un
    tope determinista de propuestas.
  - **Idioma**: seguirá en inglés (deuda documentada, no corregida en
    ninguna de las dos rondas anteriores).
  - **Confidence/rationale**: recordar que `confidence` en el rationale es la
    confianza que el LLM declara sobre su propia observación, no la
    `confidence` de evidencia del flow (ver sección 8 del documento de
    resultado de la corrección de calidad de propuestas).
  - **Provider/modelo**: confirmar que el proveedor y modelo real
    registrados coinciden con la configuración vigente; ninguna de las dos
    correcciones cambió el modelo configurado.
  - **Ausencia de secretos**: revisar que no aparezcan credenciales, tokens
    ni cadenas de conexión en las propuestas o en la evidencia citada.
- `PROJECT_STATE.json`: ninguna de las dos correcciones lo modificó; el
  rerun tampoco debe escribir en él sin una decisión explícita de
  actualización de estado.

## 5. Después del rerun

No ejecutar R9 automáticamente. No declarar `V4_3_CLOSED`. Reportar los
hallazgos del rerun (si `CONTEXT_TOO_LARGE` reapareció o no, cantidad de
propuestas, diversidad observada, y cualquier desviación de lo esperado en
esta lista) como su propio resultado, separado de este documento de
instrucciones. Si `CONTEXT_TOO_LARGE` reaparece con una causa distinta a la
corregida en esta ronda (por ejemplo, un repositorio real cuya evidencia
agregada excede `SMALL`/`TINY` incluso con la selección budget-aware), eso es
un fail-closed legítimo del contrato R5, no una regresión — documentarlo
como tal y no reabrir esta corrección para "hacerlo caber" ampliando límites
o `chars_per_token` (prohibido explícitamente por ambas correcciones).
