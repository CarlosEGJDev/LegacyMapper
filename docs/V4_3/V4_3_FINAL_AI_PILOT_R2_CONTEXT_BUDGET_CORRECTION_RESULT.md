# V4.3 — Corrección de regresión de budget de contexto (rerun R2)

Ejecuta `prompts/V4_3/V4_3_FINAL_AI_PILOT_R2_CONTEXT_BUDGET_CORRECTION_PROMPT.md`.

Estado de entrada: V4.3 R0–R8 aprobados, `CopilotProvider` real y distribución
limpia validados, corrección de diversidad de propuestas aplicada
(`docs/V4_3/V4_3_FINAL_AI_PILOT_PROPOSAL_QUALITY_CORRECTION_RESULT.md`), suite
posterior en 2121/1989/0/0/132. Se ejecutó el rerun real R2. R9 no se ejecuta
en esta tarea; V4.3 no se declara cerrada.

---

## 1. Evidencia del rerun real R2

```text
status: PARTIAL
ai_requested: true
ai_invoked: false
proposal_count: 0
proposal_review_status: NO_PROPOSALS_GENERATED
canonical_knowledge_produced: false
technical_lead_approval: false
```

```text
AI_INTERPRETATION: FAILED
PROPOSAL_GENERATION: SKIPPED_DUE_TO_UPSTREAM_FAILURE
```

Error exacto:

```text
CONTEXT_TOO_LARGE:
budget_insufficient:profile=SMALL;
budget_insufficient:profile=TINY
```

`ai_invoked: false`, `provider_id: null`, `model_id: null` — el proveedor
nunca fue invocado; el fallo ocurrió enteramente en la capa determinista de
selección/budgeting, antes de `CopilotProvider`.

---

## 2. Cadena exacta selection → budget (inspeccionada antes de modificar)

1. `run_ai_interpretation` (`legacy_documenter/orchestration/ai_interpretation.py:124`)
   llama a `_build_within_budget(indexes, source_snapshot, flow_ids, profile,
   limit)`.
2. `_build_within_budget` (línea 246) intenta `attempts = [profile] +
   [PROFILE_REDUCTION[profile]]` — para el perfil por defecto `SMALL`:
   `["SMALL", "TINY"]`. Para cada intento:
   a. `select_flow_ids(indexes, PROFILES[attempt_profile][0])`
      (`legacy_documenter/context/ai_projection.py`) — perfil `SMALL` = 80
      flows máx.; `TINY` = 20.
   b. `AiProjectionBuilder.build(scoped, indexes, ..., profile=attempt_profile)`
      hidrata cada flow (`EvidenceHydrator.hydrate_flow`) y llama a
      `AiProjectionBuilder.package(records, ..., profile=attempt_profile)`.
   c. `_build_request(package)` construye el `LLMRequest`.
   d. `measure_request_payload(request, FINDING_SCHEMA)` mide el payload
      serializado final (incluye `SYSTEM_INSTRUCTION`/`USER_INSTRUCTION`,
      envelope, records, schema — no solo la estimación interna del paquete).
   e. Si `package["statistics"]["completeness"] == "BUDGET_INSUFFICIENT"`,
      se registra `budget_insufficient:profile=<perfil>` y se continúa al
      siguiente perfil (línea 277-279). Si `metrics["payload_estimated_tokens"]
      > limit`, se registra el motivo equivalente y también se continúa
      (línea 280-285).
   f. Si ambos intentos fallan, `run_ai_interpretation` reporta
      `CONTEXT_TOO_LARGE` con el mensaje concatenado de ambos motivos —
      exactamente el string observado en el rerun real.

Este orden (`select_flow_ids -> hydration -> package -> request
serialization -> budget validation`) es el mismo de antes de esta corrección;
no se modificó su secuencia.

---

## 3. Causa raíz demostrada

`AiProjectionBuilder.package` (`legacy_documenter/context/ai_projection.py`)
ordena los registros ya hidratados con `_bucketed_order` (introducido por la
corrección de diversidad anterior), que prioriza los buckets más ricos
primero (bucket 0: terminal resuelto o escritura/transacción confirmada;
bucket 3: sin operaciones, terminal unresolved). Después de ordenar, un bucle
`for` **greedy** iba incorporando candidatos mientras cupieran en
`max_chars`, pero **abortaba (`break`) en el primer candidato que no cabía**,
sin probar los siguientes de la lista aunque fueran mucho más pequeños.

Al priorizar los flows más ricos primero, un único flow muy grande (muchas
rutas/operaciones de datos confirmadas) puede terminar primero en el orden.
Si ese único candidato ya excede `max_chars` por sí solo, el `break` deja
`chosen = []` sin haber probado ningún otro candidato — resultado:
`completeness = "BUDGET_INSUFFICIENT"`. Esto ocurre igual en `SMALL`
(16.000 caracteres) y en `TINY` (4.000 caracteres), porque el candidato
oversized encabeza el orden en ambos perfiles (la reducción de perfil solo
cambia cuántos flows se consideran, no el orden relativo entre ellos).

### Reproducción determinista (sin fixtures reales del piloto)

Fixture sintética con 4 flows: `FLOW-BIG` (bucket 0, ~167.756 caracteres
hidratado — deliberadamente enorme), `FLOW-MED` (bucket 0, ~1.398
caracteres), `FLOW-MIX` (bucket 1, ~1.855 caracteres), `FLOW-TRIV` (bucket 3,
~1.364 caracteres). Ejecutando el algoritmo **anterior** (`break` en el
primer candidato que no cabe) directamente sobre esos 4 registros:

```text
OLD SMALL -> BUDGET_INSUFFICIENT []
OLD TINY  -> BUDGET_INSUFFICIENT []
```

Ejecutando el algoritmo **corregido** (`continue` en vez de `break`) sobre el
mismo fixture:

```text
SMALL -> TRUNCATED   records included: ['FLOW-MIX', 'FLOW-MED', 'FLOW-TRIV']
TINY  -> TRUNCATED   records included: ['FLOW-MIX', 'FLOW-MED']
```

Esto demuestra la causa raíz de forma reproducible: un solo candidato
oversized bloqueaba completamente ambos perfiles con el algoritmo anterior;
con el algoritmo corregido, se salta ese candidato y el resto se empaqueta
normalmente. `FLOW-BIG` no aparece en ninguna salida (excluido por tamaño,
tal como exige el objetivo 2 del prompt: nunca invocar al provider con un
request fuera de presupuesto).

El caso real conocido `FLOW-0343552547` (~27.969 tokens estimados con el
provider real) confirma que un flow individualmente rico y grande puede
seguir cabiendo por sí solo si el perfil se lo permite — el problema nunca
fue que un flow grande no pudiera nunca ser enviado, sino que un flow grande
bloqueaba a todos los demás cuando quedaba primero en el orden.

---

## 4. Algoritmo anterior

```python
for record, cost in zip(capped, costs):
    extra = cost + (1 if chosen else 0)
    if envelope_chars + used + extra > max_chars:
        break          # <- aborta todo el empaquetado
    chosen.append(record)
    used += extra
```

`take first N que quepan hasta el primer fallo` — exactamente el patrón que
la sección 6 del prompt prohíbe ("no usar take first N ni stop on first
oversized si existen candidatos posteriores que caben").

---

## 5. Algoritmo nuevo

Un único cambio de una palabra clave, en el mismo bucle, sin tocar el orden
de prioridad por buckets ni el desempate:

```python
for record, cost in zip(capped, costs):
    extra = cost + (1 if chosen else 0)
    if envelope_chars + used + extra > max_chars:
        continue       # <- salta este candidato, prueba el siguiente
    chosen.append(record)
    used += extra
```

Efecto: un candidato que no cabe se descarta individualmente (nunca se
trunca ni se parte) y el recorrido continúa por el resto de `capped` en el
mismo orden de diversidad ya establecido. `insufficient = bool(capped) and
not chosen` sigue siendo la condición de `BUDGET_INSUFFICIENT` — solo se
alcanza cuando **ningún** candidato de la lista cupo, preservando el
fail-closed exigido (sección 6.6 y T2).

También se ajustó `minimum_required_characters` (una estadística informativa,
no parte del contrato de selección) de `envelope + costs[0]` a
`envelope + min(costs)`, porque con la nueva lógica el primer elemento del
orden ya no es necesariamente el candidato más pequeño posible — el mínimo
real es el que mejor describe "el paquete más chico que podría construirse
con al menos un registro". Ningún test existente fijaba el valor anterior.

No se tocó `select_flow_ids`, `_bucketed_order`, `_flow_richness_bucket`,
`_record_richness_bucket`, ni ningún criterio de diversidad de la corrección
previa — la selección sigue siendo tan diversa como antes; solo cambió cómo
se aplica el presupuesto de caracteres sobre esa selección ya ordenada.

---

## 6. Atomicidad de evidencia

Ningún flow se parte para caber: un candidato o se incluye completo (el
registro hidratado exacto que produce `EvidenceHydrator.hydrate_flow`, sin
tocar `paths`, `terminals`, `data_operations`, `transactions` ni
`evidence_refs`) o se excluye entero. Verificado por **T8**
(`test_included_records_are_byte_identical_to_a_fresh_hydration`): cada
registro en `package["records"]` es `==` a una nueva hidratación directa del
mismo `flow_id`.

---

## 7. SMALL / TINY

El fallback `SMALL -> si no cabe, TINY -> si tampoco cabe, CONTEXT_TOO_LARGE`
se preserva sin cambios de contrato (`_build_within_budget` no fue
modificado). Lo que cambió es que ahora cada perfil puede realmente
construir su propio paquete válido a partir de su propia selección
(en vez de fallar espuriamente por un único candidato oversized). Verificado
por:
- **T1**: un candidato oversized se excluye; los demás se seleccionan tanto
  en `SMALL` como en `TINY`.
- **T2**: cuando *todos* los candidatos exceden individualmente el
  presupuesto (incluso el más grande posible), `BUDGET_INSUFFICIENT` en
  ambos perfiles y `CONTEXT_TOO_LARGE` sin llamar al proveedor — el
  fail-closed sigue intacto.
- **T3**: el fallback real preexistente SMALL→TINY (por límite de payload
  final, no por tamaño de un único candidato) sigue funcionando: con un
  límite de tokens del payload final entre lo que necesita `SMALL` (80 flows)
  y lo que necesita `TINY` (20 flows), el primer intento (`SMALL`) se
  rechaza y el segundo (`TINY`) se acepta, exactamente en ese orden.
- **T4**: un dataset mixto que cabe en `SMALL` no dispara un segundo intento
  a `TINY` (un único `build()` observado vía spy).

---

## 8. Diversidad bajo budget

El orden por buckets de riqueza (0 rico → 3 trivial) se conserva íntegro; lo
único que cambió es que un candidato que no cabe ya no bloquea a los
siguientes. Esto significa que, bajo presupuesto ajustado, la selección
final sigue prefiriendo representar buckets ricos cuando individualmente
caben, y solo recurre al bucket trivial cuando queda espacio disponible
después de los más ricos — **T7**
(`test_final_package_still_carries_richer_flows_after_pruning`) verifica que
la selección final tras el recorte de presupuesto sigue incluyendo
`FLOW-B`/`FLOW-C` (buckets 0/1) y no queda reducida solo a `FLOW-D`
(bucket 3). No se alteró `confidence` en ningún punto (**T9**).

---

## 9. Tests

`tests/test_v4_3_final_ai_pilot_r2_context_budget_correction.py` (15 tests
nuevos), cubriendo T1–T11 del prompt:

- **T1** (2) — candidato oversized en bucket 0 excluido; candidatos menores
  seleccionados en `SMALL` y en `TINY`.
- **T2** (2) — todos los candidatos individualmente demasiado grandes:
  `BUDGET_INSUFFICIENT` directo y `CONTEXT_TOO_LARGE` sin llamar al
  provider.
- **T3** (1) — fallback real `SMALL` falla / `TINY` sucede bajo un límite de
  payload final ajustado.
- **T4** (1) — `SMALL` exitoso no dispara reintento a `TINY`.
- **T5** (1) — la medición usada para decidir es exactamente
  `measure_request_payload(request, FINDING_SCHEMA)` sobre el request
  final construido.
- **T6** (1) — misma entrada produce siempre mismos ids/orden/perfil/métricas.
- **T7** (1) — la diversidad sobrevive al recorte por presupuesto.
- **T8** (1) — evidencia atómica: registro incluido == hidratación fresca.
- **T9** (1) — sin mutación de `confidence`.
- **T10** (2) — `CONTEXT_TOO_LARGE` se reporta sin invocar
  `_ExplodingProvider` (ni a nivel de `_build_within_budget` ni a nivel de
  `run_ai_interpretation` completo).
- **T11** (2) — superficie pública de `ai_projection`/`ai_interpretation`
  preservada.

---

## 10. Resultados

Tests específicos de esta corrección:

```text
Ran 15 tests
OK
```

Suites V4.3 relevantes (R5, R6, R7, R8, corrección de calidad de propuestas,
esta corrección, e integración V4.2-R4 de propuestas):

```text
Ran 243 tests
OK
```

Suite completa (`python -m unittest discover -s tests`):

```text
total:    2136
passed:   2004
failed:   0
errors:   0
skipped:  132
```

(Baseline previo: 2121 tests, 1989 passed, 0 failed, 0 errors, 132 skipped —
la diferencia es exactamente los 15 tests agregados por esta corrección;
`0 failed`/`0 errors` se mantiene.)

---

## 11. Runtime Independence

- `ai_projection.py` sigue sin importar `legacy_documenter.llm` ni ningún
  proveedor (sin cambios respecto a la corrección anterior; el cambio es de
  una palabra clave dentro de un bucle puro sobre estructuras en memoria).
- Los tests T2/T10 confirman que `CONTEXT_TOO_LARGE` se reporta sin invocar
  `_ExplodingProvider`, tanto a nivel de `_build_within_budget` como del
  punto de entrada de producción `run_ai_interpretation`.
- Ningún test de esta corrección llama a Copilot real, red, ni ningún
  `LLMProvider` real.

**RUNTIME INDEPENDENCE: PASS**

---

## 12. Restricciones verificadas

| Restricción | Estado |
|---|---|
| No modificar `CopilotProvider` | Cumplido — no tocado |
| No modificar `requirements-copilot.txt` | Cumplido — no tocado |
| No modificar distribution builder | Cumplido — no tocado |
| No modificar `consumer_projection.py` | Cumplido — no tocado |
| No modificar `hydration.py` | Cumplido — no tocado |
| No modificar `ProviderRegistry` | Cumplido — no tocado |
| No modificar V5 / Plugin Runtime / detección de tecnología | Cumplido — no tocados |
| No modificar `PROJECT_STATE.json` | Cumplido — no tocado |
| No modificar renderers de documentación humana | Cumplido — no tocados |
| No modificar R8 presentation logic | Cumplido — no tocado |
| No ejecutar R9 | Cumplido |
| No declarar V4.3 cerrada | Cumplido |
| No cambiar límites/`chars_per_token`/`measure_request_payload`/output reservation/schema reservation/context window | Cumplido — `ai_interpretation.py` no fue modificado |
| No truncar evidencia nueva de paths/terminals/data operations/evidence_refs | Cumplido — T8 verifica igualdad byte-a-byte con hidratación fresca |
| Selección determinista, sin LLM/red/random para budgeting | Cumplido |
| No llamar Copilot real desde tests | Cumplido (T2, T10) |
| No abordar idioma inglés de AI proposals ni renombrado UX de `confidence` | Cumplido — fuera de alcance, no tocado |

**RESTRICTIONS: PASS**

---

## 13. Deuda residual

- Las mismas dos deudas ya documentadas en la corrección de calidad de
  propuestas anterior siguen abiertas y explícitamente fuera de alcance de
  esta ronda: idioma inglés de `AI_PROPOSALS.json`, y la colisión de
  nomenclatura de `confidence` en el rationale de una propuesta frente a la
  `confidence` de evidencia del flow.
- No se detectó ninguna deuda nueva de alcance ampliado durante esta
  corrección: el fix fue estrictamente el cambio de `break` a `continue`
  descrito en la sección 5, sin necesidad de tocar `select_flow_ids`,
  `_bucketed_order`, ni ningún criterio de diversidad.

---

## 14. Estado final

```text
V4_3_READY_FOR_FINAL_AI_PILOT_R3
```

No se ejecutó R9. No se declaró V4.3 cerrada. No se ejecutó el piloto real
(instrucciones para R3 en `docs/V4_3/V4_3_FINAL_AI_PILOT_R3_INSTRUCTIONS.md`).
