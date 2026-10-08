# LegacyMapper V5.7 — R3 Final Verification + Closure + Commit + Push
## Approval + Canonical Knowledge

## 1. Objetivo

Cerrar V5.7 en una única ronda final.

R1 fue implementada.
R2 corrigió dos defectos reales y quedó aprobada:

1. stale detection en primera decisión;
2. preservación immutable del proposal revisado.

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

NO iniciar V5.8.

## 2. Estado de partida

Base publicada V5.6:

`14280cf8e42700be3105999f463733ebfa88b4a9`

Estado V5.7 esperado antes de R3:

```text
V5_7_IN_PROGRESS
latest_completed_round = V5.7-R2
latest_approved_round = V5.6-R3
V5_7_R2_READY_FOR_HUMAN_REVIEW
human_review = PENDING
v5_7_closed = false
```

R1: `COMPLETED`.
R2: `COMPLETED / APPROVED_FOR_R3`.
No existe R2.1/R2.2.

Puede existir como modificación administrativa local posterior al push de V5.6:
`docs/V5/V5_6_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Preservarla e incluirla si sigue correcta.

## 3. Autorización

El usuario autoriza en esta ronda:
- verificación final;
- corrección mínima solo si aparece defecto de cierre;
- actualización de docs/estado;
- staging explícito;
- UN commit local;
- `git push origin main`;
- consultas Git necesarias.

NO autoriza tag, release, force push, amend, rebase, reset destructivo, clean, eliminación de ramas ni iniciar V5.8.

Si el push falla: no force, no rebase automático, no merge improvisado; documentar y detenerse.

## 4. Fuentes obligatorias

Leer `AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.json`, cierres/contratos V5.0–V5.6, los entregables V5.7 R1/R2, ambos roadmaps/continuidad, implementación `legacy_documenter/review/`, CLI review, proposal/reset logic y tests V5.7.

Regla:

```text
R3 verifica y cierra.
No rediseña V5.7.
```

## 5. Freeze de producción

Congelar producción V5.7. No cambiar decision semantics, IDs, canonical model, ReviewBaseline, proposal snapshot contract, provider abstraction, Evidence Core, segmentation ni iniciar V5.8.

Si aparece un defecto real: corregirlo, documentarlo y repetir validaciones afectadas.

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

Confirmar branch `main`, HEAD/origin en base V5.6, cambios V5.7 locales, sin outputs/cache/IST/temp/secrets y sin V5.8. No hacer staging aún.

## 7. HumanDecision

Revalidar `HUMAN_DECISION 1.0` y acciones `APPROVE/REJECT/CORRECT/DEFER`.

Confirmar reviewer obligatorio, sanitización, decision_id estable, `decided_at` fuera de identidad, `baseline_id` presente y proposal immutable.

## 8. ReviewBaseline

Revalidar `ReviewBaseline` con baseline_id, proposal_id, proposal_fingerprint, evidence_snapshot, evidence_fingerprint, scope, reviewer y created_at.

Confirmar:
- `review prepare` crea baseline;
- prepare repetido = no-op;
- baseline identity no depende de timestamp/reviewer;
- first decision requiere baseline;
- sin baseline → `BASELINE_REQUIRED`;
- no write parcial antes del error.

## 9. Stale-first-review

Reprobar explícitamente:

```text
proposal sobre evidence A
prepare baseline A
evidence cambia a B
refs siguen existiendo
first APPROVE
→ PROPOSAL_STALE
```

También first CORRECT stale → `PROPOSAL_STALE`, y proposal cambiada → `PROPOSAL_TAMPERED`.

## 10. Optimistic recheck

Confirmar que justo antes de persistir se revisan firmas/stat relevantes; si cambió, se recarga y recomputa evidence fingerprint; si difiere, falla sin escribir snapshot/decision/canonical.

## 11. Immutable proposal snapshot

Revalidar `REVIEW_PROPOSAL_SNAPSHOT 1.0` en `knowledge/review_snapshots/PRP-*.json`.

Debe preservar proposal normalizada completa, proposal_id/fingerprint, status, metadata, evidence_refs, scope, partial metadata, provenance provider/model/context/request identity, baseline_id y evidence snapshot/fingerprint. Sin source crudo ni prompts.

## 12. Snapshot idempotency/tamper

```text
same proposal_id + same fingerprint → no-op
same proposal_id + different fingerprint → PROPOSAL_TAMPERED/conflict
```

Nunca overwrite silencioso.

## 13. Full/reset survival

Re-ejecutar:

```text
proposal artifact
→ prepare
→ decision
→ snapshot
→ canonical si aplica
→ legacy cleanup elimina proposals/
→ snapshot intacto
→ decision intacta
→ canonical intacto
→ audit chain resuelve
```

No cambiar cleanup legacy salvo defecto nuevo real.

## 14. Audit chain

Revalidar:

```text
canonical → decision → proposal snapshot → baseline → evidence fingerprint/snapshot
```

Para REJECT/DEFER: `decision → proposal snapshot → baseline`.

Eslabón faltante = error explícito.

## 15. Canonical semantics

Revalidar `CANONICAL_KNOWLEDGE 1.0`:
- APPROVE → canonical;
- CORRECT → canonical humano corregido;
- REJECT/DEFER → no canonical;
- Evidence y Proposal intactas;
- Decision y Canonical separados;
- no auto-approval;
- no auto-canonicalization.

## 16. CORRECT

Confirmar correction humana explícita, sin provider, schema estricto, refs validadas, scope respetado, `corrected_from` preservado y autoría humana marcada.

Observación aceptada: refs nuevas de CORRECT no tienen estado previo en baseline; se validan contra evidence actual y scope.

## 17. Partial semantics V5.6

Canonical/snapshot segmentados conservan:

```text
partial=true
parent_flow_id
segment_id
included/omitted metadata
scope
```

Nunca convertir aprobación de segment en knowledge global del parent. No semantic auto-merge.

## 18. Grounding

Confirmar refs válidas, scope consistente, unknown/malformed refs rechazadas, correction refs fuera de scope rechazadas, provider sin autoridad de aprobación y Evidence confidence/status sin cambios.

## 19. Idempotency y transitions

Revalidar same decision no-op, duplicate terminal incompatible error, invalid transition error, DEFER continuable, no duplicate canonical y repair idempotente si decision existe y canonical faltó tras fallo parcial.

## 20. Persistence

Confirmar artifacts:

```text
knowledge/baselines/
knowledge/review_snapshots/
knowledge/decisions/
knowledge/canonical/
knowledge/REVIEW_VIEW.md
```

Atomic write, stable ordering, schemas, no overwrite silencioso, readback exacto y sin secrets/source crudo.

## 21. CLI

Revalidar:

```text
main.py review list
main.py review prepare
main.py review decide
main.py review canonical
```

Reviewer explícito, decide exige baseline, `--chain` funciona, errores estables y sin provider resolution.

## 22. Provider boundary

Durante toda R3:

```text
REAL_PROVIDER_CALLS = 0
REAL_LLM_CALLS = 0
```

Confirmar `_resolve_provider` no invocado.

## 23. Evidence immutability

Verificar hashes antes/después de prepare y de las cuatro acciones, más cleanup. Esperado: Evidence/index unchanged.

## 24. Architecture guards

Confirmar que Evidence no importa review; orchestration no auto-aprueba; llm no depende de canonical store; segmentation no depende de review; review no importa provider/tecnología concretos; full pipeline no auto-aprueba.

## 25. Tests dirigidos R3

Ejecutar mínimo V5.7 R1/R2, V5.6 segmentation, V5.5 generic AI, proposal integration, real-provider guard, cache/fingerprint, Evidence invariants, maintainability/inventory y baseline V4-R14 relevante.

Baseline R2 dirigido:

```text
439 tests
0 failures
0 errors
0 skips
```

## 26. Suite completa

```text
python -X utf8 -m unittest discover -s tests
```

Baseline R2:

```text
3009 tests
0 failures
0 errors
132 skips
```

Criterio: 0 failures, 0 errors.

## 27. E2E cuatro acciones

Revalidar sobre COPIAS controladas V5.5/V5.6:

```text
prepare → APPROVE
prepare → REJECT
prepare → CORRECT
prepare → DEFER
```

Verificar canonical solo APPROVE/CORRECT, snapshot en las cuatro, audit chain, partial preservado, index intacto, artifacts originales intactos y provider calls 0.

## 28. Cleanup survival

Después del E2E eliminar `proposals/` en la copia, mantener `knowledge/`, hacer readback/chain y continuar review si contrato lo permite. Debe funcionar desde snapshot.

## 29. Determinism

Con clock fijo: mismos inputs → mismo árbol knowledge byte a byte; baseline IDs, decision IDs, snapshot bytes y canonical IDs/bytes iguales.

Con timestamp real, solo campos auditables esperados cambian.

## 30. IST regression sin approval

R2 ya dejó evidencia oficial equivalente. R3 puede reutilizarla si producción relevante está congelada, hashes coinciden, output R2 íntegro y source IST coincide.

Baseline R2:

```text
SUCCESS
ai_requested=false
ai_invoked=false
review_invoked=false
knowledge_created=false
real_provider_calls=0
47523 files
2828066791 bytes
added=0
removed=0
changed=0
```

No repetir full run innecesariamente.

## 31. Source integrity

Esperado:

```text
15138 files
SHA256 = 77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5
```

Si cambia, detenerse.

## 32. Fingerprints/cache

Confirmar analyzer version 3 y fingerprint `4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6`.

Review/canonical no entra en extraction cache ni cambia analyzer fingerprint.

## 33. Performance sanity

R2 observado:
- baseline create ~14 ms;
- baseline load/stale revalidation ~13 ms;
- decide incl snapshot ~28.5 ms;
- snapshot readback ~0.4 ms;
- IST EvidenceIndex load ~8 s (observación no bloqueante).

## 34. Maintainability

Revalidar especialmente `review/baseline.py`, `review/service.py`, `review/store.py`, `cli/review_command.py`.

Criterios: responsabilidades separadas, sin provider/technology imports, sin cambios innecesarios en pipeline/Evidence/segmentation, inventario actualizado.

## 35. Security

Confirmar secrets redacted, reviewer/rationale/correction sanitizados, snapshots sin prompts/source crudo, correction tratada como data, provider/network calls 0 y artifacts históricos originales no mutados.

## 36. Deuda final

Esperado:

RESOLVED:
- first approval without verifiable baseline;
- reviewed proposal deletable without immutable snapshot.

BLOCKING: `[]`.

FUTURE_PHASE permitido: inter-process lock, UI/RBAC, signatures, quorum, bulk review, advanced query, semantic multi-segment merge, explicit canonical supersede.

OBSERVATION: IST index load ~8s; new refs in CORRECT sin historic baseline state; unused legacy V4 in-memory approval/canonical coexist.

## 37. PROJECT_STATE

Si todo pasa:

```text
current_version = V5.7
status = V5_7_CLOSED
latest_completed_round = V5.7-R3
latest_approved_round = V5.7-R2
round_status = CLOSED
human_review = APPROVED
v5_7_closed = true
r1 = COMPLETED
r2 = COMPLETED
r3 = COMPLETED
next_version = V5.8
next_round = V5.8-R1
V5_8_READY_TO_START = true
v5_8_started = false
```

## 38. Continuidad

Actualizar: V5.7 R1 completed; revisión humana detectó dos defectos; R2 corrected and approved; R3 completed; V5.7 CLOSED; V5.8 READY_TO_START. Preservar historia.

## 39. Documento final

Crear:
`docs/V5/V5_7_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Recomendado:
`docs/V5/V5_7_R3_FINAL_VERIFICATION_AND_CLOSURE.json`

Debe cubrir contrato, ReviewBaseline, stale-first-review, optimistic recheck, proposal snapshot, cleanup survival, audit chain, canonical semantics, CORRECT, partial, grounding, idempotency, persistence, CLI, architecture/provider guards, Evidence immutability, tests, E2E, determinism, IST regression, source/fingerprints, performance, maintainability, security, deuda, estado y Git.

## 40. Staging

Antes:

```text
git status --short
git diff --stat
git diff --check
```

NO usar `git add .` sin revisión.

Incluir por rutas explícitas producción V5.7, tests R1/R2, docs R1/R2/R3, JSON/inventories, prompts R1/R2/R3, PROJECT_STATE, roadmaps/continuity y recibo post-push V5.6 correcto.

Excluir output/cache/IST/temp/logs/__pycache__/secrets.

## 41. Commit

Crear UN commit.

Mensaje recomendado:

```text
feat(v5.7): add human approval and canonical knowledge
```

Alternativa:

```text
feat(v5.7): add audited human review and canonical knowledge
```

No amend. Registrar hash, parent, stat y archivos.

## 42. Push

Ejecutar:

```text
git push origin main
```

Sin force. Si falla: `V5_7_R3_PUSH_BLOCKED`.

## 43. Verificación remota

Ejecutar:

```text
git status -sb
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
git log -1 --oneline
```

Confirmar HEAD == origin/main == remote, ahead=0, behind=0.

## 44. Tag

NO crear tag. Registrar `TAG_NOT_CREATED_BY_INSTRUCTION`.

## 45. Working tree final

Ideal clean. Si queda solo recibo post-push autorreferencial en cierre R3, documentarlo y no crear segundo commit.

## 46. Estados finales permitidos

Éxito:

```text
V5_7_CLOSED
V5_7_R3_PUSHED_TO_ORIGIN_MAIN
V5_8_READY_TO_START
```

Bloqueo técnico: `V5_7_R3_BLOCKED`.
Bloqueo solo push: `V5_7_R3_PUSH_BLOCKED`.

## 47. Criterio de cierre

V5.7 queda cerrada si R2 está aprobada, first review siempre tiene baseline verificable, stale/tamper se distinguen, proposal snapshot immutable sobrevive cleanup, audit chain es reconstruible, las cuatro acciones son correctas, partial se preserva, Evidence permanece intacta, no hay auto-approval/auto-canonicalization, provider calls=0, suite completa verde, IST sin approval equivalente, BLOCKING=[], PROJECT_STATE/continuidad cerrados, commit único y push exitoso, remoto==HEAD, sin tag y V5.8 READY_TO_START pero no iniciada.

Detenerse para revisión humana final.
