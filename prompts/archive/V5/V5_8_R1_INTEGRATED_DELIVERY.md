# LegacyMapper V5.8 — R1 Integrated Delivery
## Consumer / Plugin Contract

## 1. Objetivo

Implementar V5.8 en una sola ronda integrada siguiendo el patrón vigente:

```text
R1 — Integrated Delivery
R2 — Targeted Corrections solo si son necesarias
R3 — Final Verification & Closure
```

Objetivo oficial de V5.8:

> Formalizar el contrato de consumidores y mantener separado `Plugin Contract` de `Plugin Runtime`.

Regla del roadmap:

```text
Consumidores desacoplados.
Plugin Runtime no entra automáticamente.
```

Principio central:

```text
Core produce conocimiento/proyecciones estables
→ Consumer Contract define qué puede leer y pedir
→ Plugin Contract describe compatibilidad/capacidades
→ Runtime de plugins queda fuera de scope salvo evidencia técnica imprescindible
```

NO implementar un sistema dinámico de plugins por conveniencia.

---

## 2. Estado de partida

V5.7 está cerrada y publicada.

Commit efectivo:

`bf901dcefcf8c4b100adbe40421e231d2299c7eb`

Estado esperado:

```text
V5_7_CLOSED
V5_7_R3_PUSHED_TO_ORIGIN_MAIN
V5_8_READY_TO_START
v5_8_started = false
```

Puede existir como única modificación administrativa local post-push:

`docs/V5/V5_7_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Preservarla.

---

## 3. Fuentes obligatorias

Leer antes de diseñar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos/cierres V5.0–V5.7
- ambos roadmaps/continuidad
- `legacy_documenter/context/consumer_projection.py`
- `legacy_documenter/context/ai_projection.py`
- `legacy_documenter/context/hydration.py`
- `legacy_documenter/documentation_v52/`
- `legacy_documenter/evidence/`
- `legacy_documenter/review/`
- `legacy_documenter/knowledge/`
- cualquier `plugin_projection`, consumer registry, renderer/profile, exporter o query facade existente
- CLI relevante
- tests de consumer projection, templates, AI context, review/canonical, output compatibility.

Regla:

```text
medir antes de diseñar
```

---

## 4. Gate A — Baseline empírico de consumidores

Inventariar consumidores reales existentes.

Como mínimo clasificar:

- human-functional;
- human-technical;
- ai-context;
- JSON/exporters;
- canonical/review readers;
- CLI;
- cualquier plugin-like projection heredada;
- tests/tools que consumen artifacts.

Para cada consumidor medir/documentar:

```text
consumer_id
input actual
output actual
dependencias
imports del core
acoplamientos
schema asumido
versionado
capabilities necesarias
si muta o solo lee
```

No diseñar contrato sin este inventario.

---

## 5. Medir acoplamiento actual

Detectar consumers que conocen directamente:

- layout interno de `index/`;
- implementación de Evidence;
- provider concreto;
- adapter concreto;
- rutas físicas;
- V5.6 internals;
- V5.7 persistence internals.

Clasificar:

```text
ACCEPTABLE
MIGRATE_TO_CONTRACT
LEGACY_COMPAT
OUT_OF_SCOPE
```

No migrar todo por reflejo.

---

## 6. Gate B — Contrato mínimo

Diseñar un contrato versionado para consumidores.

Conceptualmente:

```text
ConsumerDescriptor
ConsumerRequest
ConsumerCapability
ConsumerContext
ConsumerResult
```

Los nombres pueden adaptarse.

Objetivo:

```text
consumer
→ pide una proyección/capacidad
→ recibe contrato estable
→ no navega internals arbitrarios
```

---

## 7. ConsumerDescriptor

Debe declarar como mínimo:

```text
consumer_id
consumer_version
contract_version
capabilities_required
input_kinds
output_kinds
read_only
```

Opcional si hace falta:

```text
supports_partial
supports_canonical
supports_evidence
supports_ai_proposals
```

No mezclar configuración específica de provider/tecnología.

---

## 8. Consumer capabilities

Definir capacidades explícitas, por ejemplo:

```text
READ_EVIDENCE
READ_FLOW
READ_PARTIAL_FLOW
READ_AI_CONTEXT
READ_CANONICAL
READ_REVIEW_HISTORY
RENDER_HUMAN_DOC
EXPORT_JSON
```

No asumir que todos los consumers ven todo.

La lista final debe salir del baseline real.

---

## 9. ConsumerRequest

Debe expresar:

- consumer identity;
- requested capability;
- scope;
- entity ids;
- projection/profile;
- include/exclude options permitidas;
- contract version.

No permitir que consumers pasen código ejecutable.

---

## 10. ConsumerContext

Entregar solo datos permitidos por capability.

Debe preservar:

- evidence refs;
- provenance;
- unresolved;
- partial semantics;
- canonical provenance;
- schema/version.

No exponer secretos, prompts o credenciales.

---

## 11. ConsumerResult

Debe ser versionado y explícito.

Como mínimo:

```text
consumer_id
contract_version
capability
status
payload
provenance
```

Errores deben ser contractuales, no tracebacks internos.

---

# PLUGIN CONTRACT

## 12. Separación formal

Definir:

```text
Plugin Contract
≠
Plugin Runtime
```

Plugin Contract describe:

- identidad;
- versión;
- compatibilidad;
- capabilities requeridas;
- input/output kinds;
- permisos declarativos;
- determinism/read-only flags;
- contract version.

Plugin Runtime sería:

- discovery dinámico;
- import/load de código;
- sandbox;
- lifecycle;
- install/uninstall;
- isolation;
- dependency resolution;
- signing;
- remote execution.

Eso NO entra automáticamente en V5.8.

---

## 13. Plugin manifest

Diseñar un manifest declarativo mínimo.

Conceptualmente:

```text
plugin_id
plugin_version
plugin_contract_version
requires
provides
read_only
entrypoint_metadata
```

IMPORTANTE:

`entrypoint_metadata` no implica cargar/ejecutar plugins en V5.8.

Puede existir solo como metadata reservada o quedar fuera si no hace falta.

---

## 14. Compatibilidad

Definir reglas claras:

```text
contract major incompatible
contract minor compatible si additive
unknown required capability → reject
unknown optional capability → ignore/documentar
```

No hacer fallback silencioso.

---

## 15. Version negotiation

Implementar solo si el baseline demuestra necesidad.

Mínimo aceptable:

```text
supported_contract_versions
requested_contract_version
resolved_contract_version
```

Fail closed si incompatible.

No construir semver engine complejo.

---

## 16. Read-only boundary

Por defecto:

```text
consumer/plugin contract = read-only
```

V5.8 no debe permitir:

- mutar Evidence;
- aprobar proposals;
- crear canonical;
- modificar cache;
- alterar source;
- invocar provider por permiso implícito.

Si alguna capability futura requiere write:

- declararla fuera de scope.

---

## 17. Canonical Knowledge consumer

V5.8 debe permitir leer canonical knowledge mediante contrato estable sin conocer internals de `knowledge/`.

Debe preservar:

- canonical_id;
- source proposal;
- decision;
- evidence refs;
- partial;
- provenance.

No exponer archivos internos como API pública.

---

## 18. Review history consumer

Permitir lectura contractual de:

- decisions;
- audit chain;
- proposal snapshot;
- baseline metadata.

Read-only.

No ejecutar `APPROVE/REJECT/CORRECT/DEFER` desde plugin contract.

Eso sigue siendo Human Review API explícita.

---

## 19. Evidence consumer

Permitir lectura de Evidence mediante proyección estable.

No obligar a consumers a conocer:

- adapter WebForms/Oracle;
- clases internas;
- paths físicos de cache.

Conservar IDs/provenance/unresolved.

---

## 20. Flow consumer

Debe soportar:

```text
complete flow
partial flow segment
```

Para partial preservar:

```text
partial=true
parent_flow_id
segment_id
included_paths
omitted_paths
evidence_refs
```

Nunca esconder partial.

---

## 21. AI-context consumer

V5.5/V5.6 ya tienen AI context/budget/segmentation.

V5.8 debe envolverlo como capability sin mover lógica del provider.

No duplicar:

- budget;
- segmentation;
- grounding.

Consumer contract llama a una proyección existente.

---

## 22. Human documentation consumer

Preservar V5.2:

```text
Profile
Template
Renderer
```

Consumer contract no reemplaza templates.

Debe poder pedir:

```text
human-functional
human-technical
```

sin acoplarse al engine interno.

---

## 23. JSON/export consumer

Si existe export estable, representarlo como capability.

No cambiar outputs legacy salvo necesidad demostrada.

---

## 24. Consumer registry

Si hace falta, implementar registry de descriptors/capabilities.

Debe ser:

- deterministic;
- instance-scoped o immutable;
- sin import dinámico de plugins;
- sin network;
- sin side effects.

No construir plugin loader.

---

## 25. Plugin registry vs runtime

Permitido:

```text
manifest registry
```

No permitido en V5.8 salvo evidencia fuerte:

```text
importlib dynamic plugin loading
filesystem plugin discovery
pip installation
remote plugins
process sandbox
```

Si existe tooling legacy con algo similar, medir y aislar; no expandir.

---

## 26. Error model

Errores conceptuales:

```text
UNKNOWN_CONSUMER
UNSUPPORTED_CONTRACT_VERSION
UNSUPPORTED_CAPABILITY
INVALID_SCOPE
ENTITY_NOT_FOUND
PARTIAL_NOT_SUPPORTED
CANONICAL_NOT_AVAILABLE
INVALID_REQUEST
READ_ONLY_VIOLATION
PLUGIN_MANIFEST_INVALID
PLUGIN_INCOMPATIBLE
```

Adaptar nombres al proyecto.

Fail closed.

---

## 27. Determinismo

Mismo:

```text
consumer request
+ same source artifacts
+ same contract version
```

debe producir:

```text
same result identity/order/bytes
```

cuando no contiene timestamps humanos.

No usar random UUID.

---

## 28. Result identity

Si hace falta persistir/exportar resultados:

```text
consumer_result_id = hash(contract + consumer + capability + scope + source identities)
```

No provider/model salvo capability AI específica donde forme parte natural de la identidad.

---

## 29. Persistence

Preferir on-demand.

No crear otra cache sin evidencia.

Si se persiste manifest/registry:

- schema version;
- sorted deterministic output;
- atomic write;
- write-if-changed.

---

## 30. Security

Plugin Contract es data, no código.

No ejecutar:

- manifest content;
- entrypoint string;
- template arbitrario;
- shell command.

No persistir:

- tokens;
- credentials;
- raw prompts;
- source crudo innecesario.

---

## 31. Runtime independence

Agregar guard:

```text
core analysis
evidence
cache
adapters
review
```

no dependen de plugin runtime.

Y:

```text
consumer contract
```

no depende de concrete technology/provider.

---

## 32. Backward compatibility

Si V5.8 no se usa:

```text
existing pipeline outputs unchanged
```

Existing consumers deben poder continuar.

Introducir facade/projection antes que ruptura.

---

## 33. Migration strategy

Para cada consumer actual:

```text
KEEP
ADAPT
WRAP
DEPRECATE_LATER
```

No migrar consumidores históricos sin beneficio.

Documentar qué consumer queda usando legacy path y por qué.

---

## 34. Tests sintéticos

Crear tests para:

- valid descriptor;
- unknown consumer;
- unsupported contract version;
- supported capability;
- unsupported capability;
- invalid scope;
- evidence read;
- complete flow;
- partial flow;
- canonical read;
- review history read;
- human-functional;
- human-technical;
- AI-context;
- deterministic ordering;
- read-only guard;
- invalid plugin manifest;
- plugin incompatible;
- no runtime/plugin loading;
- no provider/technology coupling.

---

## 35. Fake plugin/consumer

Crear un Fake consumer/plugin manifest determinista.

Debe probar:

```text
manifest
→ contract validation
→ capability request
→ ConsumerResult
```

Sin cargar código externo.

Sin red.

---

## 36. Real IST proof

Sobre output IST verificable:

ejecutar al menos:

- evidence lookup;
- one complete flow;
- one partial/segmented flow;
- one human documentation projection;
- canonical lookup si existe artifact controlado local;
- AI-context projection sin provider call.

No persistir contenido sensible en docs; solo IDs/métricas.

---

## 37. Plugin Contract proof

Demostrar:

```text
valid manifest
→ accepted

unknown required capability
→ rejected

incompatible contract version
→ rejected

manifest tries write capability
→ rejected
```

No ejecutar entrypoint.

---

## 38. No Plugin Runtime proof

Agregar guard/test que demuestre ausencia de:

- `importlib`/dynamic import para plugins;
- plugin directory scanning;
- install/uninstall;
- subprocess plugin execution;
- remote plugin fetch;
- plugin network execution.

Si existe tooling legacy con algo similar, clasificarlo y aislarlo.

---

## 39. Architecture guard

Debe quedar:

```text
Evidence/Core
→ projection/facade
→ Consumer Contract
→ consumer
```

No:

```text
consumer
→ internal resolver/provider/adapter arbitrario
```

Y:

```text
Plugin Manifest
→ Contract Validator
```

NO:

```text
Plugin Manifest
→ Runtime Loader
```

---

## 40. Cache/fingerprint

Consumer/plugin contract NO debe cambiar:

```text
ANALYZER_VERSION = 3
ANALYZER_CODE_FINGERPRINT = 4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6
```

salvo que se toque upstream analysis, lo cual no debería ocurrir.

No invalidar extraction cache.

---

## 41. AI/provider boundary

Tests y pruebas V5.8:

```text
REAL_PROVIDER_CALLS = 0
REAL_LLM_CALLS = 0
```

V5.8 no necesita provider real.

Fake AI context puede reutilizar artifacts existentes.

---

## 42. Approval boundary

Consumer/plugin contract puede LEER canonical/review.

No puede:

- auto-APPROVE;
- auto-CORRECT;
- crear canonical;
- saltar ReviewBaseline.

Agregar guard.

---

## 43. Performance

Medir:

- descriptor validation;
- capability resolution;
- evidence lookup;
- flow projection;
- canonical read;
- human-doc projection.

Evitar O(N²).

No hacer full scan por request si puede usar índices existentes.

---

## 44. Maintainability

Auditar before/after.

Preferir módulos pequeños:

```text
consumers/contracts.py
consumers/registry.py
consumers/facade.py
plugins/contracts.py
plugins/validation.py
```

solo si encajan con arquitectura real.

No crear abstracciones vacías.

---

## 45. Deuda permitida

FUTURE_PHASE aceptable:

- dynamic plugin runtime;
- plugin installation;
- sandbox/process isolation;
- signing/trust store;
- remote plugin registry;
- permissions/RBAC;
- hot reload;
- third-party packaging;
- plugin lifecycle;
- V5.9 second-tech validation.

No implementar por adelantado.

---

## 46. Tests dirigidos

Ejecutar:

- nuevos V5.8;
- consumer projection;
- V5.2 docs/profile/template;
- V5.5 AI contract;
- V5.6 segmentation;
- V5.7 review/canonical;
- Evidence invariants;
- cache/fingerprint;
- real-provider guard;
- maintainability.

Registrar conteos/duración.

---

## 47. Suite completa

Ejecutar:

```text
python -X utf8 -m unittest discover -s tests
```

Baseline V5.7:

```text
3009 tests
0 failures
0 errors
132 skips
```

Criterio:

```text
0 failures
0 errors
```

---

## 48. IST regression

Ejecutar o reutilizar evidencia solo si producción upstream permanece congelada y es verificable.

Objetivo:

```text
V5.8 contract present
but unused
→ legacy outputs unchanged
```

Esperado:

```text
added = 0
removed = 0
changed = 0
```

No ampliar exclusiones.

---

## 49. Definition of Done R1

R1 lista si:

- baseline real de consumers;
- consumer contract versionado;
- capabilities explícitas;
- facade/projection estable;
- plugin manifest contract;
- compatibility validation;
- read-only by default;
- no plugin runtime;
- Evidence/flows/partial/canonical/review/docs/AI context consumibles;
- partial preservado;
- approval boundary preservado;
- provider boundary preservado;
- Fake consumer/plugin contract E2E;
- IST proof;
- full suite verde;
- legacy outputs equivalentes;
- 0 provider calls;
- ninguna deuda BLOCKING.

---

## 50. R2 solo si hace falta

Abrir R2 solo ante defecto real:

- consumer aún depende de internals críticos;
- partial se pierde;
- plugin contract ejecuta código;
- write capability accidental;
- review/canonical pueden mutarse desde plugin;
- provider/technology coupling;
- incompatible version aceptada silenciosamente;
- regression IST;
- suite roja.

No abrir R2 por:

- plugin runtime;
- UI;
- signing;
- remote registry;
- install/uninstall;
- V5.9.

Si R1 queda limpia:

```text
R1 → R3
```

---

## 51. PROJECT_STATE

Al finalizar R1:

```text
current_version = V5.8
status = V5_8_IN_PROGRESS
latest_completed_round = V5.8-R1
latest_approved_round = V5.7-R3
round_status = V5_8_R1_READY_FOR_HUMAN_REVIEW
human_review = PENDING
v5_8_closed = false
next = HUMAN_REVIEW
```

No marcar V5.8 cerrada.

---

## 52. Continuidad

Actualizar:

- V5.7 CLOSED;
- V5.8 R1;
- Plugin Contract separado de Plugin Runtime;
- R2 solo si defecto real;
- V5.9 no iniciada.

---

## 53. Git

R1:

- consultas permitidas;
- NO commit;
- NO push;
- NO tag;
- NO amend;
- NO rebase;
- NO reset destructivo;
- NO clean.

Registrar:

- branch;
- HEAD;
- origin/main;
- ahead/behind;
- cambios;
- recibo post-push V5.7 si existe.

---

## 54. Entregables

Crear:

`docs/V5/V5_8_R1_INTEGRATED_DELIVERY.md`

Recomendado:

`docs/V5/V5_8_R1_INTEGRATED_DELIVERY.json`

Opcional:

`docs/V5/V5_8_R1_CONSUMER_PLUGIN_INVENTORY.json`

El Markdown debe incluir:

1. Objetivo.
2. Estado inicial.
3. Fuentes.
4. Baseline consumers.
5. Acoplamiento actual.
6. Diseño.
7. ConsumerDescriptor.
8. Capabilities.
9. ConsumerRequest.
10. ConsumerContext.
11. ConsumerResult.
12. Plugin Contract vs Runtime.
13. Plugin manifest.
14. Compatibility/versioning.
15. Read-only boundary.
16. Evidence consumer.
17. Flow/partial consumer.
18. AI-context consumer.
19. Human documentation consumer.
20. Canonical consumer.
21. Review-history consumer.
22. Registry/facade.
23. Errors.
24. Determinism.
25. Persistence.
26. Security.
27. Runtime independence.
28. Compatibility/migration.
29. Synthetic tests.
30. Fake consumer/plugin.
31. Real IST proof.
32. Plugin contract proof.
33. No-runtime proof.
34. Architecture guards.
35. Cache/fingerprint.
36. Provider/approval guards.
37. Performance.
38. Maintainability.
39. Debt.
40. Directed tests.
41. Full suite.
42. IST regression.
43. PROJECT_STATE.
44. Continuidad.
45. Git.
46. Recomendación R2/R3.
47. Estado final.

---

## 55. Estados finales permitidos

Éxito:

```text
V5_8_R1_READY_FOR_HUMAN_REVIEW
```

y exactamente una recomendación:

```text
V5_8_NEXT_R2_TARGETED_CORRECTIONS
```

o:

```text
V5_8_NEXT_R3_FINAL_VERIFICATION
```

Bloqueo:

```text
V5_8_R1_BLOCKED
```

---

## 56. Regla final

Ejecutar en esta misma ronda:

```text
medir consumers reales
→ diseñar consumer/plugin contract
→ implementar facade/registry mínimo
→ validar Fake consumer/plugin
→ probar consumers reales
→ corregir
→ suite completa
→ regresión IST
→ documentar
```

No cargar plugins dinámicamente.

No implementar Plugin Runtime.

No activar providers reales.

No iniciar V5.9.

Detenerse para revisión humana.
