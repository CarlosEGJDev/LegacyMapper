# LegacyMapper V5.8 — R3 Final Verification + Closure + Commit + Push
## Consumer / Plugin Contract

## 1. Objetivo

Cerrar V5.8 en una única ronda final.

R1 fue aprobada humanamente y R2 no es necesaria.

Secuencia:

```text
verificación final
→ regresión mínima
→ cierre documental
→ actualización de estado
→ staging explícito
→ commit único
→ push a origin/main
→ verificación remota
```

NO iniciar V5.9.

## 2. Estado de partida

V5.7 está cerrada y publicada.

Commit base publicado:

`bf901dcefcf8c4b100adbe40421e231d2299c7eb`

R1 V5.8 aprobada:

```text
V5_8_R1_READY_FOR_HUMAN_REVIEW
V5_8_NEXT_R3_FINAL_VERIFICATION
```

R2:

```text
NOT_REQUIRED
```

Estado esperado antes de R3:

```text
current_version = V5.8
status = V5_8_IN_PROGRESS
latest_completed_round = V5.8-R1
latest_approved_round = V5.7-R3
human_review = PENDING
v5_8_closed = false
plugin_runtime = NOT_IMPLEMENTED
```

Puede existir como única modificación administrativa local posterior al push de V5.7:

`docs/V5/V5_7_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Preservarla e incluirla si sigue correcta.

## 3. Autorización

El usuario autoriza en esta ronda:

- verificación final;
- actualización documental/estado;
- staging explícito;
- UN commit local;
- `git push origin main`;
- consultas Git necesarias.

NO autoriza:

- tag;
- release;
- force push;
- amend;
- rebase;
- reset destructivo;
- clean;
- eliminación de ramas;
- iniciar V5.9;
- implementar Plugin Runtime.

Si el push falla: no usar force, rebase automático ni merge improvisado; detenerse y documentar.

## 4. Fuentes obligatorias

Leer antes de ejecutar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos/cierres V5.0–V5.7
- `docs/V5/V5_8_R1_INTEGRATED_DELIVERY.md`
- `docs/V5/V5_8_R1_INTEGRATED_DELIVERY.json`
- `docs/V5/V5_8_R1_CONSUMER_PLUGIN_INVENTORY.json`
- ambos roadmaps/continuidad
- `legacy_documenter/consumers/`
- `legacy_documenter/plugins/`
- `legacy_documenter/review/store.py`
- tests V5.8 y guards históricos relevantes.

Regla:

```text
R3 verifica y cierra.
No rediseña V5.8.
```

## 5. Freeze de producción

Antes de validar:

- congelar producción V5.8;
- no cambiar consumer contract;
- no cambiar plugin contract;
- no cambiar capability set;
- no cambiar result identity;
- no cambiar review/canonical semantics;
- no tocar Evidence Core;
- no tocar segmentation;
- no tocar provider abstraction;
- no introducir persistence/cache;
- no crear CLI nuevo;
- no implementar Plugin Runtime;
- no iniciar V5.9.

Si aparece un defecto técnico real, corregirlo, documentarlo y repetir las validaciones afectadas.

## 6. Preflight Git

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

Confirmar:

- branch `main`;
- HEAD = origin/main = commit base V5.7;
- cambios V5.8 aún locales;
- no outputs/cache/IST/temp;
- no secretos;
- no V5.9.

No hacer staging aún.

## 7. Consumer Contract 1.0

Revalidar que siga siendo:

```text
read-only
versioned
deterministic
provider-neutral
technology-neutral
```

## 8. ConsumerDescriptor

Revalidar:

```text
consumer_id
consumer_version
contract_version
capabilities_required
input_kinds
output_kinds
read_only
```

Confirmar campos obligatorios, unknown keys rechazadas, `read_only=true`, capabilities/kinds validados.

## 9. Capability set

Congelar exactamente:

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

No agregar ni quitar capabilities en R3.

## 10. ConsumerRequest / ConsumerResult

Revalidar request identity, scope, entity_ids, profile y opciones permitidas. Sin callables ni objetos arbitrarios.

`CONSUMER_RESULT` debe preservar:

- consumer_id;
- contract version;
- capability;
- status;
- payload;
- provenance;
- source identities;
- read_only;
- partial/completeness cuando aplique.

Errores contractuales, sin traceback ni secretos.

## 11. Result identity

Confirmar identidad content-derived, sin UUID ni timestamp:

```text
hash(contract + consumer + capability + scope + entities + profile + options + source identities)
```

## 12. Plugin Contract != Plugin Runtime

Guard obligatorio:

```text
Plugin Contract
≠
Plugin Runtime
```

V5.8 implementa solo manifest/compatibilidad/capability validation/read-only contract.

NO implementar:

- discovery dinámico;
- import/load;
- install/uninstall;
- lifecycle;
- sandbox/isolation;
- dependency resolution;
- signing;
- remote execution;
- remote registry;
- hot reload.

## 13. Plugin manifest

Revalidar:

```text
plugin_id
plugin_version
plugin_contract_version
requires
provides
read_only
entrypoint_metadata?
```

`entrypoint_metadata` es texto inerte: nunca se ejecuta, resuelve ni importa.

## 14. Compatibility/versioning

Confirmar:

```text
major incompatible → reject
same major additive minor → resolve
unknown required capability → reject
unknown optional capability → ignore + report
write-like capability → reject
read_only=false → reject
```

Fail closed.

## 15. No-runtime proof

Re-ejecutar guard AST y confirmar ausencia de loaders/discovery/exec/network/subprocess. Cualquier coincidencia permitida debe quedar documentada como no-runtime.

## 16. READ_EVIDENCE

Confirmar IDs, kind, record, fingerprint, unresolved y provenance. Entity inexistente → `ENTITY_NOT_FOUND`.

## 17. READ_FLOW

Confirmar:

```text
partial=false
completeness=COMPLETE
```

## 18. READ_PARTIAL_FLOW

Revalidar:

```text
partial=true
parent_flow_id
segment_id
included_paths
omitted_paths
evidence_refs
```

Cobertura completa, no overlap, provenance.partial=true.

## 19. PARTIAL_NOT_SUPPORTED

Revalidar fail-closed del caso donde el budget no permite segmentar:

```text
PARTIAL_NOT_SUPPORTED
BUDGET_IMPOSSIBLE_AFTER_SEGMENTATION
```

## 20. READ_AI_CONTEXT

Confirmar que envuelve `AiProjectionBuilder` existente y no duplica budget, segmentation, grounding ni provider logic.

Provider resolution = 0.

## 21. RENDER_HUMAN_DOC

Revalidar `human-functional` y `human-technical`; hashes/manifests correctos; traversal rechazado; V5.2 intacta.

## 22. EXPORT_JSON

No cambiar `LegacyMapperConsumerProjection 1.0`.

## 23. READ_CANONICAL

Confirmar lectura por canonical_id/proposal_id/evidence_ref y preservación de provenance, decision, source proposal, partial y refs. Sin canonical → `CANONICAL_NOT_AVAILABLE`.

## 24. READ_REVIEW_HISTORY

Confirmar decisions, baselines, proposal snapshot y audit chain verificado; solo lectura; no `ApprovalService`.

## 25. Read-only proof

Re-ejecutar hash del árbol antes/después de requests representativas.

Esperado:

```text
tree hash unchanged
```

ConsumerFacade no escribe, borra, aprueba, crea canonical, muta cache ni toca source.

## 26. Approval boundary

Consumer/plugin contract puede LEER review/canonical, nunca APPROVE/CORRECT/REJECT/DEFER, create canonical, prepare ni decide.

## 27. Provider boundary

Durante R3:

```text
REAL_PROVIDER_CALLS = 0
REAL_LLM_CALLS = 0
PROVIDER_RESOLUTION_ATTEMPTS = 0
```

## 28. Technology neutrality

Paquetes puros no importan WebForms/Oracle, adapters/extractors concretos ni providers concretos.

## 29. Runtime independence

Confirmar que core/evidence/cache/adapters/review/cli/pipeline no importan `consumers` ni `plugins`.

## 30. Tests dirigidos

Ejecutar como mínimo:

- `tests.test_v5_8_r1_consumer_plugin_contract`
- consumer projection
- V5.2 docs/profile/template
- V5.5 generic AI
- V5.6 segmentation
- V5.7 review/canonical
- Evidence invariants
- cache/fingerprint
- real-provider guard
- maintainability/inventory
- hydration/budget/docs humanas relevantes.

Baseline R1:

```text
727 tests
0 failures
0 errors
0 skips
```

## 31. Suite completa

Ejecutar:

```text
python -X utf8 -m unittest discover -s tests
```

Baseline R1:

```text
3053 tests
0 failures
0 errors
132 skips
```

Criterio: 0 failures, 0 errors.

## 32. Fake plugin/consumer E2E

Re-ejecutar:

```text
manifest → validate → descriptor → registry → ConsumerFacade → ConsumerResult
```

Comprobar READ_FLOW/READ_EVIDENCE OK, capability no declarada rechazada, write rechazada, malicious entrypoint no ejecutado, no red y no dynamic loading.

## 33. Real IST proof

Revalidar sobre artifacts IST existentes, sin modificar salida:

- evidence lookup;
- complete flow;
- partial flow;
- human-functional;
- human-technical;
- AI-context;
- export manifest;
- unresolved preservado.

Baseline R1:

```text
complete flow = FLOW-0000207528
partial flow = FLOW-0152459726
399 paths
19 segments
```

Confirmar unión 399, all partial, parent ok, omitted y refs presentes.

## 34. Canonical/review controlled proof

Reutilizar artifact local controlado si sigue verificable. Confirmar canonical read, review history, audit chain, partial preservado y artifact untouched.

## 35. Determinism

Repetir requests entre instancias nuevas y con entities permutadas.

Esperado:

```text
same result_id
same bytes
same ordering
```

## 36. IST regression

R1 verificó:

```text
47523 files
2828066791 bytes
added=0
removed=0
changed=0
```

R3 NO debe repetir full run si upstream sigue congelado, analyzer fingerprint igual, `review/store.py` sigue fuera del pipeline, output verificable y source IST coincide.

Solo repetir si producción upstream cambia o aparece divergencia.

## 37. Source integrity

Esperado:

```text
15138 files
SHA256 = 77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5
```

Si cambia, detenerse.

## 38. Analyzer/cache

Confirmar:

```text
ANALYZER_VERSION = 3
ANALYZER_CODE_FINGERPRINT = 4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6
```

Consumer/plugin contract no entra en extraction cache ni invalida upstream.

## 39. Performance sanity

Usar R1 como referencia; solo alertar regresión material. No recalibrar.

## 40. Review-history complexity guard

R1 corrigió un O(N²). Revalidar que colecciones se carguen una sola vez y no haya scan por proposal.

## 41. Maintainability

Revalidar especialmente:

```text
legacy_documenter/consumers/contracts.py
legacy_documenter/consumers/registry.py
legacy_documenter/consumers/sources.py
legacy_documenter/consumers/facade.py
legacy_documenter/plugins/contracts.py
legacy_documenter/plugins/validation.py
legacy_documenter/review/store.py
```

Confirmar responsabilidades separadas, no provider/technology imports, sin runtime loader, cambio aditivo en review/store.

## 42. Security

Confirmar sanitizer, no tokens/credentials/raw prompts/source extra, no manifest execution, no traversal, no provider/network, errores sin detalles sensibles.

## 43. Deuda final

Esperado:

```text
BLOCKING = []
```

FUTURE_PHASE permitido:

- Plugin Runtime;
- install/uninstall;
- sandbox/isolation;
- signing/trust store;
- remote registry;
- permissions/RBAC;
- hot reload;
- third-party packaging;
- lifecycle;
- write capabilities;
- V5.9 multi-technology validation.

## 44. PROJECT_STATE

Si todo pasa:

```text
current_version = V5.8
status = V5_8_CLOSED
latest_completed_round = V5.8-R3
latest_approved_round = V5.8-R1
round_status = CLOSED
human_review = APPROVED
v5_8_closed = true
r2 = NOT_REQUIRED
r3 = COMPLETED
plugin_runtime = NOT_IMPLEMENTED
next_version = V5.9
next_round = V5.9-R1
V5_9_READY_TO_START = true
v5_9_started = false
```

No iniciar V5.9.

## 45. Continuidad

Actualizar:

- V5.8 R1 approved;
- R2 NOT_REQUIRED;
- R3 completed;
- V5.8 CLOSED;
- Plugin Contract cerrado;
- Plugin Runtime sigue fuera;
- V5.9 READY_TO_START.

## 46. Documento final

Crear:

`docs/V5/V5_8_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Recomendado:

`docs/V5/V5_8_R3_FINAL_VERIFICATION_AND_CLOSURE.json`

Debe cubrir contrato, capabilities, plugin/no-runtime, read-only, partial, canonical/review, provider/approval boundaries, tests, E2E, IST, determinism, performance, maintainability, security, debt, state y Git.

## 47. Staging

Antes:

```text
git status --short
git diff --stat
git diff --check
```

NO usar `git add .` sin revisión.

Incluir por rutas explícitas:

- producción V5.8;
- `review/store.py` aditivo;
- tests V5.8;
- pins históricos legítimamente actualizados;
- docs R1/R3;
- JSON/inventory R1;
- prompts R1/R3;
- PROJECT_STATE;
- roadmaps/continuidad;
- recibo post-push V5.7 correcto.

Excluir output/cache/IST/temp/logs/__pycache__/secrets.

## 48. Commit

Crear UN commit.

Mensaje recomendado:

```text
feat(v5.8): add consumer and plugin contracts
```

No amend.

Registrar hash, parent, stat y archivos.

## 49. Push

Ejecutar:

```text
git push origin main
```

Sin force.

Si falla:

```text
V5_8_R3_PUSH_BLOCKED
```

## 50. Verificación remota

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

## 51. Tag

NO crear tag.

Registrar:

```text
TAG_NOT_CREATED_BY_INSTRUCTION
```

## 52. Working tree final

Ideal: clean.

Si queda únicamente el recibo post-push autorreferencial, documentarlo y no crear segundo commit solo por él.

## 53. Estados finales permitidos

Éxito:

```text
V5_8_CLOSED
V5_8_R3_PUSHED_TO_ORIGIN_MAIN
V5_9_READY_TO_START
```

Bloqueo técnico:

```text
V5_8_R3_BLOCKED
```

Bloqueo solo push:

```text
V5_8_R3_PUSH_BLOCKED
```

## 54. Criterio de cierre

V5.8 queda cerrada si:

- R1 aprobada;
- R2 no requerida;
- Consumer Contract 1.0 válido;
- Plugin Contract 1.0 válido;
- read-only boundary preservada;
- capabilities correctas;
- partial preservado;
- canonical/review solo lectura;
- approval boundary intacta;
- no Plugin Runtime;
- no dynamic loading;
- no provider calls;
- no technology coupling;
- determinismo preservado;
- suite completa verde;
- IST equivalente;
- analyzer/cache intactos;
- no deuda BLOCKING;
- PROJECT_STATE cerrado;
- continuidad actualizada;
- commit único;
- push exitoso;
- remoto == HEAD;
- sin tag;
- V5.9 READY_TO_START pero no iniciada.

Detenerse para revisión humana final.
