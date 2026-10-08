# LegacyMapper V5.7 — R1 Integrated Delivery
## Approval + Canonical Knowledge

## 1. Objetivo

Implementar V5.7 en una sola ronda integrada siguiendo el modelo vigente:

```text
R1 — Integrated Delivery
R2 — Targeted Corrections solo si son necesarias
R3 — Final Verification & Closure
```

Objetivo de V5.7:

> Formalizar el paso controlado desde Evidence y AI Proposal hacia Human Decision y Canonical Knowledge, sin auto-approval ni auto-canonicalization.

Contrato oficial del roadmap:

```text
Evidence
    ↓
AI Proposal
    ↓
Human Decision
    ↓
Canonical Knowledge
```

Estados humanos obligatorios:

```text
APPROVE
REJECT
CORRECT
DEFER
```

Principio central:

```text
la IA propone
el humano decide
el sistema valida y persiste
```

V5.7 NO debe permitir auto-approval, auto-canonicalization, promoción silenciosa de una propuesta, mutación de Evidence, pérdida de provenance, aceptación de propuesta stale/tampered ni usar provider/model como autoridad.

## 2. Estado de partida

V5.6 está cerrada y publicada.

Commit efectivo V5.6:

`14280cf8e42700be3105999f463733ebfa88b4a9`

Estado esperado:

```text
V5_6_CLOSED
V5_6_R3_PUSHED_TO_ORIGIN_MAIN
V5_7_READY_TO_START
```

V5.7 no iniciada.

Puede existir como única modificación administrativa local posterior al push:

`docs/V5/V5_6_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Clasificarla y preservarla.

## 3. Fuentes obligatorias

Leer antes de diseñar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos/cierres V5.0–V5.6
- `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
- cierres y entregas V5.5/V5.6
- ambos roadmaps/continuidad
- implementación real bajo `legacy_documenter/knowledge/`, `knowledge/proposals/`, `evidence/`, `orchestration/`, `context/`, `cli/`
- tests actuales de proposals, provenance, readiness, human review y persistence.

Regla:

```text
contrato aprobado
> evidencia del código actual
> este prompt
> conveniencia
```

## 4. Gate A — Baseline empírico

Antes de diseñar approval/canonical, inspeccionar el estado real.

Caracterizar como mínimo:

- modelo actual de proposal;
- proposal ID/status/review_status;
- evidence_refs y grounding;
- scope y parent_flow_id/segment_id si aplica;
- provider/model provenance;
- request identity;
- persistence actual;
- artifacts JSON/Markdown;
- readiness/human review tooling;
- código existente llamado `approval`, `canonical`, `provenance` o equivalente;
- estados heredados como `AI_PROPOSED`, `READY_FOR_REVIEW`, `PENDING_TECHNICAL_LEAD_REVIEW`.

No implementar hasta completar este inventario.

## 5. Medir propuestas reales

Usar artifacts V5.5/V5.6 verificables si existen.

Medir cantidad total, grounding válido, propuestas partial/segmentadas, estados, evidence_refs, stale verificable, tamaño y provenance provider/model/request.

No hacer provider calls reales.

## 6. Baseline de ausencia de canonical knowledge

Demostrar el comportamiento actual:

```text
proposal generated
→ review pending
→ canonical knowledge = false / absent
```

Verificar que no exista auto-promotion oculta.

Si existe vía legacy de aprobación, medirla y clasificarla; no reutilizarla ciegamente.

## 7. Gate B — Diseño mínimo

Diseñar el contrato más pequeño que satisfaga:

```text
Proposal
→ HumanDecision
→ CanonicalKnowledge
```

Contrato conceptual mínimo:

```text
HumanDecision
CanonicalKnowledgeRecord
ApprovalService
CanonicalStore
```

No construir UI web, workflow engine, RBAC empresarial, plugin API V5.8, knowledge graph completo ni semantic merge inteligente.

## 8. HumanDecision

Debe representar explícitamente:

```text
APPROVE
REJECT
CORRECT
DEFER
```

Debe incluir como mínimo:

- decision_id;
- proposal_id;
- action;
- reviewer identity;
- decided_at;
- rationale/comment opcional;
- correction payload si action=CORRECT;
- proposal fingerprint/version;
- evidence snapshot/fingerprint suficiente para stale detection;
- provenance.

Reglas:

```text
APPROVE → puede producir canonical
REJECT → nunca produce canonical
CORRECT → produce canonical desde corrección humana validada
DEFER → no produce canonical
```

## 9. Reviewer identity

No inventar autenticación completa.

El contrato debe aceptar identidad humana explícita y trazable.

Requisitos:

- no vacía;
- provider/model no puede ser reviewer;
- no permitir `AUTO` como reviewer válido;
- persistir quién decidió;
- si CLI necesita reviewer, debe ser argumento explícito sin fallback silencioso.

## 10. Proposal immutability

Una propuesta revisada es input immutable.

Antes de aceptar decisión:

- validar proposal_id;
- recomputar fingerprint;
- verificar contenido;
- verificar grounding/evidence refs/scope/partial semantics;
- detectar modificación posterior si aplica.

No modificar proposal original para convertirlo en canonical.

## 11. Stale detection

Una decisión debe fallar o requerir re-review si la propuesta ya no corresponde a la evidencia actual.

Mecanismo determinista posible:

- evidence fingerprint;
- proposal fingerprint;
- request identity;
- refs + hashes/versions;
- run identity.

Estados conceptuales:

```text
CURRENT
STALE
TAMPERED
MISSING_EVIDENCE
```

No promover stale.

## 12. APPROVE semantics

APPROVE acepta el contenido de la propuesta y, tras validar grounding/provenance, materializa canonical knowledge.

Pero:

- Evidence intacta;
- Proposal histórica intacta;
- Decision persistida aparte;
- Canonical referencia proposal + decision + evidence.

## 13. REJECT semantics

REJECT:

- persiste decisión;
- no genera canonical;
- no borra proposal;
- no borra evidence;
- no impide proposal futura sobre misma evidencia.

No convertir rechazo en unresolved evidence.

## 14. DEFER semantics

DEFER:

- persiste decisión;
- proposal continúa no-canonical;
- no genera canonical;
- conserva rationale;
- permite revisión posterior.

No tratar DEFER como REJECT.

## 15. CORRECT semantics

La corrección debe ser contenido humano explícito.

Reglas:

- no pedir a IA que corrija y autoaprobar;
- correction payload valida schema;
- conserva evidence refs pertinentes;
- refs agregadas/eliminadas se validan contra Evidence;
- canonical distingue original proposal, human correction y final canonical content;
- atribuir autoría humana correctamente.

## 16. CanonicalKnowledgeRecord

Debe ser explícito y separado de Evidence y Proposal.

Conceptualmente:

```text
canonical_id
source_proposal_id
decision_id
decision_action
content
evidence_refs
provenance
created_at
status/version
```

Puede agregar scope, parent_flow_id, segment_id, canonical type/category, corrected_from.

## 17. Canonical ID y versioning

Definir identidad estable y reproducible. Evitar random UUID salvo razón fuerte.

Debe permitir replay idempotente, detectar duplicados y distinguir una corrección posterior legítima.

No permitir overwrite silencioso. Preferir append-only o supersede explícito.

## 18. Audit trail y transitions

Decisions y canonical records deben ser auditables.

Regla fuerte:

```text
no delete/overwrite silencioso
```

Formalizar transitions según estados reales.

Prohibir duplicate APPROVE que cree canonical duplicado, APPROVED→PENDING silencioso y decisión sobre proposal inexistente.

## 19. Proposal status vs Decision

Separar:

```text
proposal lifecycle
decision history
canonical state
```

Una vista `review_status` puede derivarse, pero no ser única fuente de verdad.

## 20. Grounding obligatorio para canonical

Canonical solo puede materializarse si evidence refs existen, grounding es válido, scope consistente y la proposal/correction no cita evidencia fuera de alcance.

No canonizar proposal no-grounded.

## 21. Segmentación V5.6

Una proposal segmentada puede aprobarse, pero canonical debe conservar:

```text
partial = true
parent_flow_id
segment_id
included_paths / scope
```

Nunca transformar aprobación de segmento en knowledge global del parent.

No hacer semantic multi-segment merge automático.

## 22. Confidence y Evidence state

APPROVE/CORRECT no modifica confidence o status de Evidence Core.

Separar:

```text
evidence confidence
canonical knowledge acceptance
```

No promover unresolved a confirmed automáticamente.

## 23. Canonical provenance

Cada canonical record debe responder qué proposal lo originó, qué decision lo autorizó, quién/cuándo decidió, qué evidence refs soportan, provider/model original si aplica, correction humana, scope/segment y fingerprints/versions vigentes.

## 24. Persistence contract

Definir persistencia simple y auditable, por ejemplo:

```text
knowledge/decisions/
knowledge/canonical/
```

o artifacts equivalentes.

Requisitos:

- schema version;
- stable sort;
- atomic write;
- write-if-changed;
- no secrets;
- no source crudo;
- deterministic rendering excepto timestamp humano explícito.

## 25. Human timestamps

`decided_at` representa un acto humano real.

Debe venir de operación/clock injectable; tests usan clock fijo; no afecta Evidence fingerprints ni analysis cache.

## 26. CLI / review operation

Implementar la mínima operación utilizable para aplicar una decisión humana, por CLI o API Python coherente con arquitectura actual.

Debe aceptar explícitamente proposal, action, reviewer, rationale opcional, correction payload para CORRECT y output/run dir.

No diseñar UX extensa.

## 27. No provider calls durante approval

Approval/canonicalization es determinista y humano.

```text
provider calls = 0
LLM calls = 0
```

También para CORRECT.

## 28. Replay / idempotency y conflicts

Repetir exactamente la misma decisión no debe crear duplicados ambiguos.

Definir idempotent no-op o duplicate-decision error claro.

Mismo approved decision → mismo canonical result.

Manejar explícitamente proposal ya approved, rejected→approve, decision_id duplicado, correction sobre versión vieja, canonical conflict y stale evidence.

Fail closed.

## 29. Error model

Códigos conceptuales:

```text
PROPOSAL_NOT_FOUND
PROPOSAL_STALE
PROPOSAL_TAMPERED
MISSING_EVIDENCE
INVALID_GROUNDING
INVALID_DECISION
INVALID_TRANSITION
REVIEWER_REQUIRED
CORRECTION_REQUIRED
CORRECTION_INVALID
CANONICAL_CONFLICT
DUPLICATE_DECISION
```

Adaptar nombres a convenciones existentes.

## 30. Canonical store query

Permitir lectura determinista mínima:

- list;
- by canonical_id;
- by proposal_id;
- quizá by evidence_ref si barato.

No construir query layer completo del roadmap.

## 31. Compatibility

Preservar proposal generation, AI_PROPOSALS artifacts, review pending por defecto, V5.5 provider abstraction, V5.6 partial semantics, human docs, consumer outputs y Evidence Core.

Si nadie ejecuta approval:

```text
outputs existentes deben seguir iguales
```

## 32. Cache/fingerprints

- HumanDecision no invalida extraction cache;
- canonical knowledge no cambia analyzer fingerprint;
- proposal/evidence identity se usa para stale validation;
- approval artifacts tienen schema/version propios;
- no mezclar canonical state en extraction cache.

## 33. Security y concurrency básica

Sanitizar rationale, corrections y reviewer display data.

No persistir tokens, credentials, raw prompts, source completo ni auth headers.

No ejecutar correction content; tratarlo como datos.

Usar atomic write y fail-on-conflict/optimistic checks; no silent last-write-wins.

## 34. Tests sintéticos obligatorios

Cubrir:

### APPROVE
- grounded → canonical;
- repeated same decision;
- stale;
- tampered;
- missing evidence.

### REJECT
- persiste;
- no canonical;
- proposal retained.

### DEFER
- no canonical;
- later review possible.

### CORRECT
- correction required;
- valid corrected canonical;
- invalid refs rejected;
- correction provenance.

### Transitions/conflicts
- invalid transition;
- duplicate decision;
- canonical conflict.

### Partial
- segmented proposal sigue partial en canonical.

### Security
- sanitization;
- no secrets.

## 35. Real proposal proof

Usar una proposal real/reutilizable V5.5/V5.6 o fixture realista ya aprobado para testing.

No aprobar producción real “de verdad” sin consentimiento humano específico.

Para R1, usar COPIA controlada y demostrar APPROVE/REJECT/CORRECT/DEFER sobre copias independientes.

No modificar artifact histórico original.

## 36. Human approval boundary

Tests pueden simular decisiones humanas con fixtures.

Pero producción debe requerir acción humana explícita.

Nunca:

```text
pipeline termina IA
→ ApprovalService(APPROVE) automático
```

Agregar guard arquitectónico/test.

## 37. Canonical knowledge is not Evidence

Agregar test/guard:

```text
canonical write
→ Evidence bundle SHA unchanged
```

Canonical refiere Evidence; no la muta.

## 38. Metrics

Si corresponde, registrar solo métricas seguras:

- reviewed;
- APPROVE/REJECT/CORRECT/DEFER counts;
- canonical records created;
- stale rejections;
- conflicts;
- invalid decisions.

No incluir rationale/correction completos en RUN_SUMMARY.

## 39. Documentation/rendering

Generar vista humana mínima de pending proposals, decisions y canonical knowledge si encaja naturalmente.

No rediseñar V5.2 templates.

## 40. Architecture guard

Impedir:

- Evidence Core → approval;
- Evidence Core → canonical;
- provider implementation → canonical store;
- AI orchestration → automatic approval;
- segmentation → canonical mutation.

Permitido:

```text
knowledge/proposals
→ knowledge/approval
→ knowledge/canonical
```

o equivalente.

## 41. Tests dirigidos y suite completa

Ejecutar tests dirigidos de approval/canonical + proposals + grounding + segmentation + fingerprints + security.

Luego:

```text
python -X utf8 -m unittest discover -s tests
```

Baseline V5.6:

```text
2935 tests
0 failures
0 errors
132 skips
```

Criterio R1:

```text
0 failures
0 errors
```

## 42. Real IST regression — sin approval

Ejecutar/regresar IST con approval NO invocado.

Objetivo:

```text
V5.7 presente
pero ningún humano decide
→ outputs existentes iguales
```

Reutilizar baseline V5.6 si verificable.

Esperado:

```text
added = 0
removed = 0
changed = 0
```

para outputs existentes.

Approval/canonical artifacts no deben aparecer si no se ejecuta review.

## 43. Approval E2E controlado

Ejecutar flujo local controlado:

```text
proposal artifact copy
→ human decision fixture
→ validation
→ decision persistence
→ canonical persistence si corresponde
→ readback
```

Hacerlo para las cuatro acciones.

Sin red. Sin provider.

## 44. Determinism and audit proof

Con clock fijo:

- mismo input + misma decision → bytes iguales;
- stable ordering;
- IDs reproducibles;
- canonical readback exacto.

Con timestamp real, solo campos auditables esperados cambian.

## 45. Performance sanity

Medir validation, decision persist, canonical materialization y readback.

No ejecutar approval masivo si no hay volumen real que lo justifique.

## 46. Maintainability

Auditar before/after knowledge modules, proposals, approval, canonical, provenance, CLI changes e imports.

Evitar un único módulo gigante.

Separar `models/service/store/validation` solo si el tamaño real lo justifica.

## 47. Deuda permitida

Clasificar:

```text
BLOCKING
FUTURE_PHASE
OBSERVATION
```

Puede quedar FUTURE_PHASE:

- UI de revisión;
- RBAC;
- firma criptográfica;
- multi-reviewer quorum;
- bulk approval;
- semantic merge multi-segment;
- canonical graph/query avanzado;
- plugin API V5.8;
- cross-tech V5.9.

## 48. Definition of Done R1

R1 queda lista si:

- HumanDecision explícito;
- APPROVE/REJECT/CORRECT/DEFER;
- reviewer requerido;
- proposal immutable;
- stale/tamper detection;
- grounding obligatorio;
- canonical separado;
- audit semantics;
- partial V5.6 preservado;
- Evidence no mutada;
- approval sin provider;
- E2E de cuatro acciones;
- suite verde;
- IST sin approval equivalente;
- 0 auto-approval;
- 0 auto-canonicalization;
- 0 provider calls en approval;
- ninguna deuda BLOCKING.

## 49. R2 solo si hace falta

Abrir R2 solo ante defecto real:

- auto-approval posible;
- stale proposal aprobable;
- Evidence mutada;
- CORRECT sin provenance;
- partial perdido;
- canonical overwrite silencioso;
- duplicate approvals duplican canonical;
- provider llamado durante approval;
- regression IST;
- suite roja.

No usar R2 para UI, RBAC, firmas, plugin API, V5.8 o V5.9.

Si R1 queda limpia:

```text
R1 → R3
```

## 50. PROJECT_STATE

Al finalizar R1:

```text
current_version = V5.7
status = V5_7_IN_PROGRESS
latest_completed_round = V5.7-R1
latest_approved_round = V5.6-R3
round_status = V5_7_R1_READY_FOR_HUMAN_REVIEW
human_review = PENDING
v5_7_closed = false
next = HUMAN_REVIEW
```

No marcar V5.7 cerrada.

## 51. Continuidad

Actualizar solo estado vigente/ledger.

Registrar V5.6 CLOSED, V5.7 R1 y modelo máximo 3 rondas.

No reescribir historia.

## 52. Git

En R1:

- consultas permitidas;
- NO commit;
- NO push;
- NO tag;
- NO amend;
- NO rebase;
- NO reset destructivo;
- NO clean.

Registrar branch, HEAD, origin/main, ahead/behind, archivos modificados/nuevos y recibo post-push V5.6 si existe.

## 53. Entregables

Crear:

`docs/V5/V5_7_R1_INTEGRATED_DELIVERY.md`

Recomendado:

`docs/V5/V5_7_R1_INTEGRATED_DELIVERY.json`

Opcional:

`docs/V5/V5_7_R1_APPROVAL_CANONICAL_INVENTORY.json`

El Markdown debe incluir baseline proposal/knowledge, diseño, HumanDecision, reviewer, immutability, stale/tamper, cuatro acciones, canonical record, identity/versioning, audit/transitions, grounding, partial semantics, Evidence immutability, provenance, persistence, CLI/API, idempotency/conflicts, errors, query/readback, cache/fingerprints, security, tests, real proposal proof, architecture guard, suite, IST regression, E2E, performance, maintainability, debt, estado, continuidad, Git y recomendación.

## 54. Estados finales permitidos

Éxito:

```text
V5_7_R1_READY_FOR_HUMAN_REVIEW
```

y exactamente una recomendación:

```text
V5_7_NEXT_R2_TARGETED_CORRECTIONS
```

o:

```text
V5_7_NEXT_R3_FINAL_VERIFICATION
```

Bloqueo:

```text
V5_7_R1_BLOCKED
```

## 55. Regla final

Ejecutar en esta misma ronda:

```text
medir proposal/knowledge actual
→ diseñar decision/canonical contract
→ implementar
→ validar cuatro decisiones
→ corregir
→ probar
→ regresión IST sin approval
→ auditar seguridad/provenance
→ documentar
```

No activar providers reales.

No aprobar automáticamente ningún artifact histórico real.

No iniciar V5.8.

Detenerse al final para revisión humana.
