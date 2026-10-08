# LegacyMapper V5.7 — R2 Targeted Corrections
## Approval + Canonical Knowledge

## 1. Objetivo

Corregir exclusivamente dos defectos detectados tras V5.7 R1:

1. stale detection incompleta en la primera decisión;
2. pérdida potencial del artifact histórico de proposal después de un `full`.

No rediseñar V5.7. No iniciar V5.8.

Flujo:

```text
confirmar defecto
→ corregir stale-first-review
→ preservar proposal histórico
→ pruebas dirigidas
→ suite completa
→ regresión IST sin approval
→ documentar
→ revisión humana
```

## 2. Estado de partida

Base publicada V5.6:

`14280cf8e42700be3105999f463733ebfa88b4a9`

Estado actual:

```text
V5_7_IN_PROGRESS
latest_completed_round = V5.7-R1
latest_approved_round = V5.6-R3
V5_7_R1_READY_FOR_HUMAN_REVIEW
```

La revisión humana cambia la ruta a:

```text
V5_7_NEXT_R2_TARGETED_CORRECTIONS
```

## 3. Fuentes obligatorias

Leer antes de modificar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- `docs/V5/V5_7_R1_INTEGRATED_DELIVERY.md`
- `docs/V5/V5_7_R1_INTEGRATED_DELIVERY.json`
- `docs/V5/V5_7_R1_APPROVAL_CANONICAL_INVENTORY.json`
- cierre V5.6
- contratos V5.1
- cierres V5.5/V5.6
- ambos roadmaps
- `legacy_documenter/review/`
- `legacy_documenter/knowledge/proposals/`
- `legacy_documenter/cli/review_command.py`
- `legacy_documenter/cli/full_pipeline.py`
- reset/cleanup de proposal artifacts
- tests V5.7 R1.

Regla:

```text
R2 corrige exactamente dos defectos.
No ampliar scope.
```

# DEFECTO A — stale detection en primera decisión

## 4. Problema

R1 detecta stale si:

- se entrega `--expected-evidence-fingerprint`; o
- existe una decisión previa con snapshot.

Pero una primera decisión sin ese fingerprint puede validar solo la evidencia actual y no demostrar que sea la misma que soportaba la proposal al revisarse.

Ventana prohibida:

```text
proposal generada
→ evidence cambia manteniendo refs
→ first APPROVE/CORRECT sin baseline previo
→ canonical
```

## 5. Corrección requerida

Toda primera decisión debe quedar ligada a un baseline immutable de review.

Contrato conceptual:

```text
ReviewBaseline
    proposal_id
    proposal_fingerprint
    evidence_fingerprint
    evidence_snapshot
    scope
    partial metadata
    reviewer
    created_at
```

Puede usarse otro nombre si encaja mejor.

Regla obligatoria:

```text
no baseline verificable
→ no APPROVE
→ no CORRECT
```

Preferencia: toda primera decisión, incluidas REJECT/DEFER, crea o usa el mismo baseline.

## 6. `--expected-evidence-fingerprint`

Puede mantenerse como guard adicional, pero no puede ser la única protección.

Opciones válidas:

- `review list` / `prepare` crea baseline y `decide` lo exige; o
- `decide` crea baseline y exige validar el fingerprint visto por el humano.

No permitir first approval sin baseline/fingerprint verificable.

## 7. Optimistic recheck

Antes de persistir decision/canonical:

1. calcular o cargar baseline;
2. recomputar evidence fingerprint actual;
3. si difiere → `PROPOSAL_STALE`.

Mantener separación:

```text
proposal cambia → PROPOSAL_TAMPERED
evidence cambia → PROPOSAL_STALE
```

# DEFECTO B — preservar proposal histórico

## 8. Problema

Un `full` posterior puede eliminar:

```text
proposals/AI_PROPOSALS.json
proposals/AI_PROPOSALS_PENDING_REVIEW.md
```

mientras `knowledge/` permanece.

Eso deja decisiones/canonical sin el artifact histórico original.

## 9. Corrección requerida

En la primera decisión, persistir una copia immutable de la proposal revisada dentro de knowledge/review.

Ruta conceptual:

```text
knowledge/proposals/PRP-....json
```

o:

```text
knowledge/review_snapshots/PRP-....json
```

Debe preservar:

- proposal completo normalizado;
- proposal_id;
- proposal_fingerprint;
- status original;
- metadata;
- evidence_refs;
- scope;
- partial metadata;
- provider/model/context provenance si existe;
- evidence snapshot/fingerprint del review.

No copiar source crudo innecesario.

## 10. Inmutabilidad/idempotencia

```text
mismo proposal_id + mismo fingerprint
→ no-op

mismo proposal_id + distinto fingerprint
→ conflict/tamper
```

Nunca overwrite silencioso.

## 11. Relación con full/reset

Preferencia:

```text
full limpia proposals operativas
knowledge snapshot permanece
```

No cambiar la limpieza legacy salvo necesidad estricta.

## 12. Audit chain

Debe ser reconstruible:

```text
CanonicalKnowledgeRecord
→ HumanDecision
→ immutable Proposal snapshot
→ evidence snapshot/fingerprint
```

Y para REJECT/DEFER:

```text
HumanDecision
→ immutable Proposal snapshot
→ evidence snapshot/fingerprint
```

# FREEZE

## 13. No tocar

No rediseñar:

- APPROVE/REJECT/CORRECT/DEFER;
- reviewer validation;
- canonical semantics;
- append-only model;
- V5.6 partial;
- grounding;
- provider abstraction;
- Evidence Core;
- segmentation;
- templates;
- V5.8.

## 14. Compatibility

Preservar:

- `review list|decide|canonical`;
- proposal generation;
- artifacts actuales;
- no-provider approval;
- Evidence immutable;
- pipeline normal sin approval.

# TESTS

## 15. Nuevos tests stale-first-review

Casos obligatorios:

```text
proposal sobre evidence A
evidence cambia a B
refs siguen existiendo
first APPROVE
→ PROPOSAL_STALE
```

Además:

- first CORRECT stale → rejected;
- REJECT/DEFER registran baseline coherente;
- expected fingerprint mismatch → stale;
- evidence unchanged → success;
- recheck antes de write;
- fixed clock deterministic.

## 16. Nuevos tests proposal snapshot

- first decision crea snapshot;
- APPROVE/REJECT/CORRECT/DEFER lo preservan;
- repeated same decision no duplica;
- mismo PRP con fingerprint distinto → conflict/tamper;
- readback exacto.

## 17. Full/reset survival

Test obligatorio:

```text
proposal artifact
→ decision
→ snapshot
→ legacy proposal cleanup
→ proposals/ eliminado
→ snapshot intacto
→ decision readback intacto
→ canonical intacto donde corresponda
```

## 18. Audit chain

Probar resolución completa:

```text
canonical
→ decision
→ proposal snapshot
→ evidence fingerprint/snapshot
```

## 19. Evidence immutability

Confirmar SHA de `index/`/Evidence sin cambios después de:

- baseline;
- decision;
- canonical;
- proposal snapshot.

## 20. Partial proposal

Proposal segmentada V5.6 debe conservar:

```text
partial=true
parent_flow_id
segment_id
scope
included/omitted metadata
```

## 21. Security/provider guard

Confirmar:

```text
REAL_PROVIDER_CALLS = 0
REAL_LLM_CALLS = 0
```

Snapshot sin secrets, auth headers, prompts completos ni source crudo innecesario.

## 22. Tests dirigidos

Ejecutar mínimo:

- V5.7 R1;
- nuevos R2;
- V5.6 segmentation;
- proposal integration;
- real-provider guard;
- cache/fingerprint;
- Evidence invariants;
- maintainability/inventory.

## 23. Suite completa

```text
python -X utf8 -m unittest discover -s tests
```

Baseline R1:

```text
2979 tests
0 failures
0 errors
132 skips
```

Criterio:

```text
0 failures
0 errors
```

# REGRESIÓN

## 24. IST sin approval

Pipeline normal debe seguir igual.

Esperado:

```text
AI requested = false
AI invoked = false
review invoked = false
knowledge created = false
added = 0
removed = 0
changed = 0
```

No agregar exclusiones.

## 25. E2E controlado

Sobre COPIAS de artifacts V5.5/V5.6:

```text
APPROVE
REJECT
CORRECT
DEFER
```

Luego simular cleanup de proposals y verificar:

- decision history;
- proposal snapshot;
- canonical donde aplica;
- readback completo;
- Evidence intacta;
- 0 provider calls.

## 26. Determinismo

Con clock fijo:

- mismos inputs → mismos bytes;
- snapshot identity estable;
- sin duplicados;
- ordering estable.

## 27. Performance

Medir:

- create/load review baseline;
- stale revalidation;
- snapshot persist/readback.

No optimizar prematuramente.

## 28. Maintainability

Auditar módulos modificados, imports y responsabilidades.

No crear un módulo gigante.

## 29. Deuda

Estas dos observaciones deben quedar RESUELTAS, no FUTURE_PHASE:

- first approval sin baseline verificable;
- proposal revisada eliminable sin snapshot.

Puede seguir FUTURE_PHASE:

- inter-process lock;
- UI/RBAC;
- signatures;
- quorum;
- bulk review;
- advanced query;
- semantic multi-segment merge.

## 30. Definition of Done R2

R2 queda lista si:

- ninguna first APPROVE/CORRECT ocurre sin baseline verificable;
- stale se detecta aunque refs sigan existiendo;
- recheck evita race simple;
- first decision preserva immutable proposal snapshot;
- full/reset no rompe audit chain;
- canonical → decision → proposal → evidence es reconstruible;
- Evidence intacta;
- partial intacto;
- provider calls = 0;
- suite verde;
- IST normal equivalente;
- BLOCKING = [].

## 31. PROJECT_STATE

Al finalizar:

```text
current_version = V5.7
status = V5_7_IN_PROGRESS
latest_completed_round = V5.7-R2
latest_approved_round = V5.6-R3
round_status = V5_7_R2_READY_FOR_HUMAN_REVIEW
human_review = PENDING
v5_7_closed = false
next = HUMAN_REVIEW
```

## 32. Continuidad

Registrar:

- V5.7 R1 realizada;
- revisión humana solicitó R2;
- R2 targeted corrections;
- máximo 3 rondas preservado.

## 33. Git

R2:

- consultas permitidas;
- NO commit;
- NO push;
- NO tag;
- NO amend;
- NO rebase;
- NO reset destructivo;
- NO clean.

## 34. Entregables

Crear:

`docs/V5/V5_7_R2_TARGETED_CORRECTIONS.md`

Recomendado:

`docs/V5/V5_7_R2_TARGETED_CORRECTIONS.json`

Opcional:

`docs/V5/V5_7_R2_REVIEW_SNAPSHOT_INVENTORY.json`

## 35. Estados finales permitidos

Éxito:

```text
V5_7_R2_READY_FOR_HUMAN_REVIEW
V5_7_NEXT_R3_FINAL_VERIFICATION
```

Bloqueo:

```text
V5_7_R2_BLOCKED
```

No crear R2.1/R2.2.

## 36. Regla final

Ejecutar:

```text
confirmar dos defectos
→ corregir baseline stale
→ preservar proposal histórico
→ probar audit chain
→ suite completa
→ validar IST
→ documentar
```

No rediseñar V5.7.
No activar providers.
No iniciar V5.8.
Detenerse para revisión humana.
