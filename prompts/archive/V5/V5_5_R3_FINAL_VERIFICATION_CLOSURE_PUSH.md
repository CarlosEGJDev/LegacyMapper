# LegacyMapper V5.5 — R3 Final Verification + Closure + Commit + Push
## Generic AI Provider + Context

## 1. Objetivo

Cerrar V5.5 en una única ronda final.

R1 ya fue aprobada humanamente y R2 no es necesaria.

Secuencia de esta ronda:

```text
verificación final
→ regresión mínima
→ cierre documental
→ actualización de estado
→ commit único
→ push a origin/main
→ verificación remota
```

NO iniciar V5.6.

## 2. Estado de partida

V5.4 está cerrada y publicada.

Commit base publicado:

`5e9085f0601db4ad68900bbbc523933c51fa5dd3`

R1 V5.5 aprobada:

```text
V5_5_R1_READY_FOR_HUMAN_REVIEW
V5_5_NEXT_R3_FINAL_VERIFICATION
```

R2:

```text
NOT_REQUIRED
```

Puede existir como modificación administrativa local posterior al push de V5.4 el recibo final de cierre. Preservarlo e incluirlo si sigue correcto.

## 3. Autorización

El usuario autoriza explícitamente en esta ronda:

- verificación final;
- actualización documental;
- staging explícito;
- UN commit local;
- `git push origin main`;
- consultas Git necesarias para verificar remoto.

NO autoriza:

- tag;
- release;
- force push;
- amend;
- rebase;
- reset destructivo;
- clean;
- eliminación de ramas;
- iniciar V5.6.

Si el push falla, no usar force, rebase automático ni merge improvisado.

## 4. Fuentes obligatorias

Leer antes de ejecutar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos/cierre V5.0
- `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
- cierres V5.1–V5.4
- `docs/V5/V5_5_R1_INTEGRATED_DELIVERY.md`
- `docs/V5/V5_5_R1_INTEGRATED_DELIVERY.json`
- `docs/V5/V5_5_R1_MAINTAINABILITY_INVENTORY.json`
- roadmaps/continuidad V5

Regla: R3 verifica y cierra; no rediseña V5.5.

## 5. Preflight Git

Ejecutar:

```text
git status --short
git status -sb
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
git diff --check
git diff --stat
```

Confirmar rama `main`, HEAD en cierre V5.4, R1 V5.5 sin commit, sin outputs/cache/temp/secretos y sin V5.6.

## 6. Freeze de producción

Antes de validar:

- congelar producción;
- no refactorizar;
- no renombrar contratos;
- no mover módulos;
- no cambiar fingerprints;
- no cambiar analyzer version;
- no agregar providers reales;
- no agregar retries/tools/streaming.

Solo corregir defecto real que impida cierre. Si se toca producción, repetir tests relevantes y suite completa; si afecta outputs deterministas, repetir comparación real.

## 7. Verificación arquitectónica final

Revalidar:

```text
domain/context
    ↓
generic AI contract
    ↓
provider implementation
```

Prohibido que Evidence Core, context neutral, knowledge/domain, generic orchestration o documentation domain importen Copilot concreto.

Permitido solo en implementación provider, registry/factory, composition root y shim legacy justificado.

Esperado:

- MIXED = 0;
- concrete provider imports en fronteras neutrales = 0;
- Evidence Core imports llm/provider = 0.

## 8. Contrato genérico final

Revalidar `AIProvider`/alias aprobado, `AIRequest`, `AIResponse`, `ProviderCapabilities`, `generate`, `capabilities`, `context_window`, `max_output_tokens`, `structured_output`, provider/model/version, lifecycle/close y error categories.

No expandir contrato sin necesidad.

## 9. Provider actual

Verificar provider productivo actual detrás del contrato. Esperado: `COPILOT`.

Debe mantener composición explícita, credenciales aisladas, timeout, cleanup, categorías de error, structured path y compatibilidad legacy.

NO llamar al provider real.

## 10. Fake provider

Revalidar Fake sin red, determinista, capabilities configurables, simple/structured response, error inyectable, request capture aislado y close idempotente.

Debe seguir atravesando pipeline real/acotado.

## 11. Registry/factory

Revalidar provider explícito, unknown→error, disabled→no resolver entorno/credenciales, sin fallback silencioso, factories lazy, Fake explícito y Gemini UNREGISTERED si así quedó en R1.

No implementar discovery/plugin runtime.

## 12. Context selection/package/budget

Verificar separación:

```text
selection → packaging → budget → invocation → validation
```

Preservar `select_flow_ids`, `AiProjectionBuilder.package`, `measure_request_payload` y request budget neutral.

Confirmar provider sin control de selección, overflow explícito, una reducción de perfil si aplica, luego `CONTEXT_TOO_LARGE`, métricas de included/excluded/completeness y no truncación silenciosa.

NO implementar V5.6 segmentation.

## 13. Grounding

Revalidar refs dentro del paquete, rechazo de refs malformed/unknown, rechazo de request identity ajena, Evidence inmutable, unresolved sin promoción, proposal separada de canonical knowledge, aprobación humana pendiente y canonicalización=false.

## 14. Structured output

Confirmar capability declarada, false→mismatch explícito, true sin asumir JSON schema nativo, parsing local genérico y validación final determinista.

## 15. Error/lifecycle

Revalidar categorías configuration, unavailable, auth, timeout, capability mismatch, invalid response, execution, rate limit y cancelled.

Confirmar close en success/error/mismatch/overflow/missing context. Cleanup no oculta resultado primario. Sin nuevo retry de invocación.

## 16. Cache/fingerprints

Confirmar:

```text
ANALYZER_VERSION = 3
ANALYZER_CODE_FINGERPRINT = sin cambio respecto V5.4/R1 V5.5
Evidence schema = 1.0
```

Provider/model/config no deben invalidar analysis/evidence cache. AICFG debe separar provider/model/version/capabilities/limits/timeout. Identidad antigua/desconocida no reutiliza output AI.

## 17. Métricas/seguridad

Confirmar métricas saneadas de requested/invoked, provider/model/version, capabilities, counts, budget, durations, usage y error category.

No registrar prompts completos, source completo, API keys, headers, credenciales ni exceptions arbitrarias con secretos.

## 18. Tests dirigidos R3

Ejecutar como mínimo:

- `tests.test_v5_5_r1_generic_ai`
- provider contract tests históricos;
- provider guard real;
- AI interpretation/proposal integration;
- context budgeting;
- fingerprint/cache tests;
- architecture/import guard;
- security tests.

Registrar total/failures/errors/skips/duración.

## 19. Suite completa

Ejecutar:

```text
python -X utf8 -m unittest discover -s tests
```

Baseline R1:

```text
2907 tests
0 failures
0 errors
132 skips
```

Criterio R3: 0 failures / 0 errors.

## 20. IST real — AI OFF

R1 ya demostró equivalencia sobre IST oficial.

R3 NO debe repetir baseline full/off si puede reutilizarse de forma verificable.

Preferencia:

- revalidar SHA/inventario de fuente oficial;
- reutilizar baseline oficial V5.4;
- reutilizar corrida R1 V5.5 si output sigue intacto y producción está congelada.

Solo ejecutar UNA corrida nueva AI OFF si hace falta para verificar cambios posteriores.

Esperado siempre:

```text
AI requested = false
AI invoked = false
provider resolution attempts = 0
real provider calls = 0
```

## 21. Comparación canónica

Usar `tools/v5_3_compare_full_incremental.py` contra baseline oficial verificable.

Esperado:

```text
added = 0
removed = 0
changed = 0
```

Exclusiones únicamente existentes: `_cache_v53/`, root `RUN_SUMMARY.json`, root `RUN_SUMMARY.md`, `index/repository.json`.

No agregar exclusiones.

## 22. Fake AI end-to-end

Repetir solo si necesario o si producción cambió. Si R1 artifact sigue verificable y producción congelada, reutilizar evidencia R1.

Debe demostrar selection→package→generic provider→structured/local validation→grounding→proposal→metrics, con 0 red/provider real, proposal grounded, review pending y canonical knowledge false.

## 23. Performance sanity

No recalibrar.

R1:

```text
V5.4 official: 657.367 s
V5.5 R1 AI OFF: 676.784 s
delta ~ +2.95%
```

Solo investigar regresión grave adicional. No benchmarkear providers reales.

## 24. Deuda final

Clasificar BLOCKING / FUTURE_PHASE / OBSERVATION.

Esperado no bloqueante: providers adicionales, Gemini unregistered, retry avanzado, streaming/tools, V5.6 segmentation, V5.7 approval, V5.8 plugin/discovery, algoritmos grandes, diagnostics históricos UnicodeDecodeError no fallidos y `manual_verify_full_pipeline` PARTIAL con finding vacío.

No abrir R2 retrospectiva.

## 25. PROJECT_STATE

Si todo pasa:

```text
current_version = V5.5
status = V5_5_CLOSED
latest_completed_round = V5.5-R3
latest_approved_round = V5.5-R1
round_status = CLOSED
human_review = APPROVED
v5_5_closed = true
r2 = NOT_REQUIRED
r3 = COMPLETED
next_version = V5.6
next_round = V5.6-R1
V5_6_READY_TO_START = true
```

Preservar contadores históricos IA globales. Registrar R3 real provider calls=0 y Fake separado de provider real.

No marcar V5.6 iniciada.

## 26. Continuidad

Actualizar únicamente estado vigente y ledger: aprobación R1, R2 NOT_REQUIRED, R3 cierre, V5.5 CLOSED y V5.6 READY_TO_START. Preservar historia y modelo de máximo 3 rondas.

## 27. Documento final

Crear:

`docs/V5/V5_5_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Recomendado:

`docs/V5/V5_5_R3_FINAL_VERIFICATION_AND_CLOSURE.json`

Debe incluir arquitectura, contrato, provider real, Fake, registry, context/budget, grounding, structured output, errors/lifecycle, cache/fingerprints, security, tests, suite, IST AI OFF, comparación, performance, deuda, estado, continuidad, Git, commit, push, remoto y próximo V5.6.

## 28. Staging

Antes:

```text
git status --short
git diff --stat
git diff --check
```

Revisar todo y agregar por rutas explícitas. NO usar `git add .` sin revisión.

Incluir producción/tests/docs V5.5, PROJECT_STATE, continuidad, prompts R1/R3, informe R3 y administrativos V5.4 correctos.

Excluir output/cache/IST/temp/logs/__pycache__/secretos.

## 29. Commit

Crear UN commit.

Mensaje recomendado:

```text
feat(v5.5): add generic ai provider contract
```

Alternativa aceptable:

```text
feat(v5.5): decouple ai provider and context
```

No amend.

## 30. Push

Ejecutar:

```text
git push origin main
```

Sin force. Si falla: `V5_5_R3_PUSH_BLOCKED`.

## 31. Verificación remota

Ejecutar:

```text
git status -sb
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
git log -1 --oneline
```

Confirmar:

```text
HEAD == origin/main == remote refs/heads/main
ahead = 0
behind = 0
```

## 32. Tag

NO crear tag.

Registrar `TAG_NOT_CREATED_BY_INSTRUCTION`.

## 33. Working tree final

Ideal: clean.

Si queda únicamente recibo post-push autorreferencial, documentarlo y no crear segundo commit solo por él.

## 34. Estados finales permitidos

Éxito:

```text
V5_5_CLOSED
V5_5_R3_PUSHED_TO_ORIGIN_MAIN
V5_6_READY_TO_START
```

Bloqueo técnico: `V5_5_R3_BLOCKED`.

Bloqueo solo push: `V5_5_R3_PUSH_BLOCKED`.

## 35. Criterio de cierre

V5.5 queda cerrada si R1 está aprobada, R2 no requerida, provider abstraction/core neutral/provider real/Fake/context-budget-grounding/structured output/error-lifecycle/cache-fingerprint están verificados, suite verde, AI OFF equivalente, 0 provider calls reales, sin deuda BLOCKING, PROJECT_STATE y continuidad cerrados, commit creado, push exitoso, remoto==HEAD, sin tag nuevo y V5.6 READY_TO_START pero no iniciada.

Detenerse para revisión humana final.
