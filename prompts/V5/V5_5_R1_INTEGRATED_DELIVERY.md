# LegacyMapper V5.5 — R1 Integrated Delivery
## Generic AI Provider + Context

## 1. Objetivo

Implementar V5.5 en una sola ronda integrada siguiendo el modelo V5.4+:

```text
R1 — Integrated Delivery
R2 — Targeted Corrections solo si son necesarias
R3 — Final Verification & Closure
```

Objetivo de V5.5:

> Desacoplar completamente el pipeline/core de un proveedor concreto de IA y formalizar un contrato genérico de provider + contexto, manteniendo grounding, determinismo y seguridad.

Contrato objetivo del roadmap:

```text
AIProvider
    generate()
    capabilities()
    context_window
    structured_output
```

Providers futuros posibles:

```text
Copilot
Claude
OpenAI
Ollama
Gemini
Fake
```

V5.5 NO debe implementar todos ellos.

Debe dejar:

- contrato genérico real;
- provider actual preservado detrás del contrato;
- Fake provider determinista para pruebas;
- selección/configuración desacoplada;
- contexto neutral y trazable;
- pipeline sin dependencia directa de Copilot concreto;
- compatibilidad con V5.1–V5.4.

## 2. Estado de partida

V5.4 está cerrada y publicada.

Commit de cierre V5.4:

`5e9085f0601db4ad68900bbbc523933c51fa5dd3`

Estado esperado:

```text
V5_4_CLOSED
V5_4_R3_PUSHED_TO_ORIGIN_MAIN
V5_5_READY_TO_START
```

Puede existir localmente el recibo administrativo post-push de V5.4; clasificarlo y preservarlo.

## 3. Principios heredados

Preservar estrictamente:

```text
Python descubre y valida.
La IA interpreta.
```

Además:

```text
Evidence ≠ AI output
AI output ≠ Canonical Knowledge
```

V5.7 seguirá siendo responsable de aprobación/canonicalización.

V5.5 NO debe auto-aprobar, auto-canonizar, alterar Evidence Core, cambiar IDs, promover unresolved ni convertir texto IA en hechos.

## 4. Fuentes obligatorias

Leer antes de diseñar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos/cierre V5.0
- `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
- cierre V5.1
- cierre V5.2
- cierre V5.3
- cierre V5.4
- continuidad/roadmap V5
- documentación histórica V4.3 de IA
- tests actuales de LLM/provider/context
- implementación real actual bajo:
  - `legacy_documenter/llm/`
  - `legacy_documenter/orchestration/`
  - `legacy_documenter/context/`
  - `legacy_documenter/documentation/`
  - `legacy_documenter/knowledge/`
  - `legacy_documenter/cli/`

Regla de precedencia:

```text
contrato aprobado
> evidencia del código actual
> este prompt
> conveniencia
```

## 5. Contrato heredado V5.1/V5.2

Preservar:

```text
Normalized Evidence → AI factual interpretation → Audience transformation → Profile → Template → Renderer

Normalized Evidence → Generic AI Provider
```

El Evidence Core no debe importar `legacy_documenter.llm.*`.

La selección/budget/context packaging puede consumir `ai_context/` o proyecciones neutrales, pero no contaminar Evidence Core con conceptos de provider.

Grounding debe seguir resolviendo a evidencia trazable.

## 6. Gate A — Baseline empírico mínimo

Antes de crear interfaces, inspeccionar el código real y producir inventario de acoplamiento provider.

Revisar como mínimo:

```text
legacy_documenter/llm/
legacy_documenter/orchestration/
legacy_documenter/context/
legacy_documenter/documentation/
legacy_documenter/knowledge/
legacy_documenter/cli/
```

Clasificar módulos/puntos de dependencia como:

- PROVIDER_CONTRACT;
- PROVIDER_IMPLEMENTATION;
- CONTEXT_CORE;
- AI_ORCHESTRATION;
- DOMAIN/KNOWLEDGE;
- LEGACY_COMPATIBILITY;
- MIXED;
- CLI/COMPOSITION.

Registrar imports directos a provider concreto, nombres/modelos hardcodeados, resolución de credenciales, selección de provider, retry/timeout, context budget, token estimation, structured output assumptions, parsing/validation y tests que monkeypatch provider concreto.

No hacer llamadas reales a IA.

## 7. Baseline funcional de IA existente

Caracterizar con Fake/mocks existentes:

- IA deshabilitada;
- provider unavailable;
- provider fake exitoso;
- respuesta inválida;
- timeout/error;
- structured response si ya existe;
- grounding;
- RUN_SUMMARY / errores / exit behavior.

Reutilizar tests históricos cuando cubran el contrato.

## 8. Gate B — Diseño mínimo

Diseñar la abstracción más pequeña que cubra el comportamiento real.

No construir un SDK universal.

Contrato mínimo conceptual:

```text
AIProvider
ProviderCapabilities
AIRequest
AIResponse
ProviderError
```

`ProviderCapabilities` debe declarar al menos:

- provider id;
- model id o modelo configurable;
- context window;
- structured output soportado/no soportado;
- metadata/version necesaria.

No inventar streaming/tools si no existe necesidad real.

## 9. generate() neutral

La invocación genérica no debe requerir tipos Copilot específicos.

Debe transportar como mínimo, según el código real:

- instrucciones/system si aplica;
- input/context;
- model/config;
- output contract esperado;
- timeout/cancellation si ya existe;
- metadata/tracing determinista.

La respuesta neutral separa contenido, provider/model metadata, usage si existe, structured result si aplica y finish/error state.

No persistir secretos.

## 10. Context contract

Formalizar:

```text
Context Selection
Context Packaging
Provider Invocation
Response Validation
```

Principios:

```text
evidence primero
budget determinista
grounding preservado
provider no decide qué evidencia es verdad
```

Preservar, si siguen vigentes:

- `select_flow_ids`;
- `AiProjectionBuilder.package`;
- `measure_request_payload`.

Mover/renombrar solo si mejora frontera sin cambiar semántica.

## 11. Budget y context window

`context_window` debe ser capacidad declarada, no magic number de provider.

Decidir determinísticamente presupuesto disponible, reserva de output, contexto a enviar y overflow behavior.

No truncar evidencia silenciosamente.

Si no cabe, reducir según política trazable o fallar explícitamente, registrando incluido/omitido.

NO implementar Rich Flow Segmentation V5.6.

## 12. Structured output

Si provider declara `structured_output=true`, usar mecanismo genérico.

Si no lo soporta, fallback explícito o capability mismatch.

No asumir JSON schema nativo universal.

La validación final sigue siendo local/determinista.

## 13. Provider actual

Preservar el provider real soportado actualmente, verificando el código real.

Referencia histórica probable: `copilot-local`.

Debe quedar detrás del contrato genérico:

- mismo comportamiento observable;
- sin imports concretos en core/orchestration neutral;
- credenciales/config aisladas;
- errores normalizados;
- capabilities declaradas;
- compatibilidad CLI/config cuando corresponda.

## 14. Fake provider obligatorio

Crear Fake determinista, sin red.

Debe soportar:

- respuesta simple;
- structured response;
- error inyectable;
- failure/timeout simulation útil;
- registro de requests;
- capabilities configurables;
- context window pequeño para budget tests.

Debe permitir probar el pipeline IA end-to-end sin red.

## 15. Registry / factory

Centralizar composición si hoy está dispersa.

Reglas:

- provider desconocido → error claro;
- no fallback silencioso a Copilot;
- no resolver credenciales si IA disabled;
- Fake solo explícito;
- core no conoce implementations.

No construir plugin runtime V5.8.

## 16. Configuración

Auditar flags/config/env existentes.

Separar:

- configuración;
- secretos;
- capabilities reportadas.

Objetivo conceptual, sin imponer formato:

```text
ai.enabled
ai.provider
ai.model
ai.timeout
ai.max_output / budget
```

No persistir API keys/tokens.

## 17. Error model

Normalizar si hace falta:

- provider unavailable;
- authentication/config missing;
- timeout;
- capability mismatch;
- invalid response;
- provider execution error.

No incluir secretos/request completo en errores.

Preservar exit semantics.

## 18. Retry

No agregar retries complejos si no existen.

Si ya existen, caracterizar y preservar detrás de la frontera correcta.

No introducir jitter/nondeterminismo en tests.

## 19. Grounding

Toda interpretación/propuesta factual conserva referencias verificables.

Revalidar:

- ninguna referencia inventada;
- unresolved no se promueve;
- provider text no modifica Evidence;
- responses separadas de canonical knowledge.

## 20. Fingerprints/cache

Regla:

- cambiar provider/model NO debe invalidar analysis/evidence cache;
- outputs IA/context dependientes sí deben distinguir configuración para evitar mezcla incorrecta.

No contaminar `ANALYZER_CODE_FINGERPRINT` con providers si análisis determinista no depende de ellos.

Probarlo.

## 21. Métricas

RUN_METRICS/RUN_SUMMARY puede registrar sin secretos:

- AI requested;
- AI invoked;
- provider id;
- model id;
- capability summary mínima;
- request/success/failure counts;
- durations;
- usage si existe;
- error category saneada.

No registrar prompts completos, source completo, keys ni authorization headers.

## 22. Gate C — Implementación

Objetivo:

```text
domain/context selection
        ↓
generic AI contract
        ↓
provider implementation
```

No:

```text
domain → Copilot concrete
context → Copilot concrete
documentation → Copilot concrete
```

Composition root sí puede construir provider seleccionado.

Usar shims/reexports solo para compatibilidad.

## 23. Guard arquitectónico

Agregar test que impida imports concretos de provider desde:

- Evidence Core;
- context neutral;
- domain/knowledge;
- generic orchestration.

Permitirlos solo en implementation, composition/factory o shim justificado.

## 24. Tests dirigidos obligatorios

Cubrir:

### Contract
- capabilities;
- context window;
- structured output;
- request/response neutral;
- error normalization.

### Registry/factory
- provider explícito;
- unknown provider;
- disabled AI;
- no credential resolution cuando disabled.

### Fake
- deterministic response;
- structured;
- error;
- small context budget.

### Context
- deterministic selection;
- budget;
- overflow;
- grounding;
- omissions explicit;
- provider cannot alter evidence.

### Compatibility
- provider actual;
- legacy imports/config;
- AI tests existentes.

### Security
- no secretos en metrics/errors;
- no raw prompt dumps;
- sanitized diagnostics.

### Architecture
- no forbidden concrete-provider imports.

## 25. Suite completa

Ejecutar:

```text
python -X utf8 -m unittest discover -s tests
```

Criterio:

```text
0 failures
0 errors
```

Corregir defectos coherentes dentro de R1. No crear micro-rondas.

## 26. Real pipeline regression — IA OFF

Ejecutar regresión real mínima sobre IST con IA deshabilitada.

Reutilizar baseline oficial V5.4 si es verificable; si no, crear una referencia mínima.

Ejecutar UNA corrida post-V5.5 AI OFF.

Comparación canónica esperada:

```text
added = 0
removed = 0
changed = 0
```

fuera solo de exclusiones contractuales ya aprobadas.

No ampliar exclusiones.

## 27. AI path regression — Fake provider

Ejecutar un flujo productivo/acotado con Fake provider:

```text
context selection
→ package
→ generic provider
→ response validation
→ interpretation/proposal artifact
→ metrics
```

Sin red.

Registrar request count, provider/model fake, capabilities, context budget, grounding y outputs.

## 28. Provider real

R1 NO requiere llamadas reales a Copilot/Claude/OpenAI.

Sin autorización explícita:

```text
REAL_PROVIDER_CALLS = 0
```

## 29. Performance sanity

IA OFF no debe degradar materialmente pipeline determinista.

Medir total/context/documentation/export relevantes.

Fake AI: selección/package/provider fake/validation.

No benchmarkear modelos reales.

## 30. Maintainability audit

Mostrar before/after:

- concrete provider imports;
- MIXED modules;
- neutral modules;
- shims;
- high-risk modules;
- deuda residual.

La separación debe ser real, no solo renombrado.

## 31. Deuda permitida

Posible deuda no bloqueante:

- solo un provider real;
- OpenAI/Claude/Ollama/Gemini aún no implementados;
- retry sofisticado;
- streaming/tools;
- V5.6 segmentation;
- V5.7 approval;
- V5.8 discovery/plugin;
- optimizaciones provider-specific.

## 32. Definition of Done R1

R1 queda lista si:

- contrato genérico real;
- provider actual detrás de él;
- Fake prueba extensibilidad;
- context/budget neutral;
- capabilities declaradas;
- structured output explícito;
- error model neutral;
- core/domain sin provider concreto;
- IA OFF equivalente en IST;
- Fake AI end-to-end pasa;
- suite completa verde;
- 0 provider calls reales;
- seguridad/grounding preservados;
- ninguna deuda BLOCKING.

## 33. R2 solo si hace falta

R2 solo ante defecto real:

- provider concreto sigue acoplado;
- provider actual roto;
- context budget incorrecto;
- secretos en métricas;
- structured output asumido universal;
- Fake no atraviesa pipeline;
- IA OFF cambia outputs;
- suite roja.

No usar R2 para implementar providers futuros ni V5.6/V5.7.

Si R1 limpia:

```text
R1 → R3
```

## 34. PROJECT_STATE

Al finalizar:

```text
current_version = V5.5
status = V5_5_IN_PROGRESS
latest_completed_round = V5.5-R1
latest_approved_round = V5.4-R3
round_status = V5_5_R1_READY_FOR_HUMAN_REVIEW
human_review = PENDING
next = HUMAN_REVIEW
v5_5_closed = false
```

## 35. Continuidad

Actualizar solo estado vigente y ledger.

Registrar V5.4 cerrada/publicada y V5.5 R1.

Mantener modelo máximo 3 rondas.

## 36. Git

En R1:

- consultas permitidas;
- NO commit;
- NO push;
- NO tag;
- NO amend/rebase/clean/reset destructivo.

Checkpoint solo tras revisión humana.

## 37. Entregables

Crear:

`docs/V5/V5_5_R1_INTEGRATED_DELIVERY.md`

Recomendado:

`docs/V5/V5_5_R1_INTEGRATED_DELIVERY.json`

Opcional:

`docs/V5/V5_5_R1_MAINTAINABILITY_INVENTORY.json`

El Markdown debe incluir baseline, diseño, contrato, context/budget, provider actual, Fake, registry, config/secrets, error model, grounding, cache/fingerprints, métricas, tests, suite, IST AI-OFF, Fake end-to-end, seguridad, maintainability, debt, estado, continuidad, Git y recomendación.

## 38. Estados finales permitidos

Éxito:

```text
V5_5_R1_READY_FOR_HUMAN_REVIEW
```

y exactamente una:

```text
V5_5_NEXT_R2_TARGETED_CORRECTIONS
```

o:

```text
V5_5_NEXT_R3_FINAL_VERIFICATION
```

Bloqueo:

```text
V5_5_R1_BLOCKED
```

## 39. Regla final

Ejecutar en esta misma ronda:

```text
medir
→ diseñar
→ implementar
→ corregir
→ probar
→ validar IA OFF
→ validar Fake AI
→ auditar
→ documentar
```

No activar providers reales.

Detenerse al final para revisión humana.
