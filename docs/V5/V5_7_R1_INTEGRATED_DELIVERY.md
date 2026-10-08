# V5.7 R1 — Integrated Delivery: Approval + Canonical Knowledge

Fecha: 2026-10-07. Estado: `V5_7_R1_READY_FOR_HUMAN_REVIEW`. Recomendación: `V5_7_NEXT_R3_FINAL_VERIFICATION`.
Evidencia estructurada: [JSON](V5_7_R1_INTEGRATED_DELIVERY.json) · inventario: [JSON](V5_7_R1_APPROVAL_CANONICAL_INVENTORY.json).

Principio: la IA propone, el humano decide, el sistema valida y persiste. Evidence → AI Proposal → HumanDecision → CanonicalKnowledgeRecord.

## 1. Estado inicial y Git

V5.6 CLOSED, publicada en `14280cf8e42700be3105999f463733ebfa88b4a9`; branch `main`, HEAD = origin/main, ahead/behind 0/0. Única modificación local previa: recibo post-push de V5.6 (`docs/V5/V5_6_R3_FINAL_VERIFICATION_AND_CLOSURE.md`), clasificado como administrativo y preservado sin cambios de fondo. R1: sin commit, push, tag, amend, rebase ni reset. Archivos modificados: `cli/parser.py`, `cli/router.py`, `main.py`, `fingerprints/configuration.py`, `tests/test_v4_1_r0_maintainability_inventory.py`, `PROJECT_STATE.json`, ambos roadmaps. Nuevos: `legacy_documenter/review/` (6 módulos), `cli/review_command.py`, `tests/test_v5_7_r1_human_review.py`, `docs/V5/V5_7_R1_*`, `prompts/V5/V5_7_R1_INTEGRATED_DELIVERY.md`.

## 2. Gate A — Baseline empírico (proposal / knowledge)

- **Proposal actual:** modelo `knowledge/proposals.Proposal` (V4-R8), id `PRP-sha256(kind, statement, method, material_ids, relation_ids, evidence_refs)`; el estado (`READY_FOR_REVIEW`), metadata y `rationale` quedan fuera de la identidad. Persistencia: `proposals/AI_PROPOSALS.json` (envelope con `status = PENDING_TECHNICAL_LEAD_REVIEW`, provider/model/`context_package_id`) + `AI_PROPOSALS_PENDING_REVIEW.md`. En propuestas segmentadas (V5.6) la metadata lleva `flow_segment` (parent, segment_id, partial, included/omitted) y `ai_request_identity`. Un `full` posterior borra los artifacts de propuestas (`reset_stale_proposal_artifacts`); `knowledge/` no se toca.
- **Código heredado `approval` / `canonical` / `provenance` (V4-R9/R10/R6):** `knowledge/approval` y `knowledge/canonical` son capas **en memoria** (sin persistencia), vocabulario `APPROVED/REJECTED/CORRECTION_REQUESTED`, autoridad única `TECHNICAL_LEAD`, requieren `SourceType/KnowledgeNature/KnowledgeStatus` y un `Proposal` en memoria; sin DEFER, sin CORRECT con contenido humano, sin stale/tamper, sin persistencia ni CLI. **Clasificación:** modelo conceptual válido pero NO reutilizable ciegamente para artifacts persistidos; ninguna ruta de producción lo invoca (`full`/`analyze` nunca crean aprobación ni canonical). No se modificó.
- **Auto-promotion oculta:** ninguna. Grep + tests: `RunResult.canonical_knowledge_produced/technical_lead_approval` siempre `False`; los estados `AI_PROPOSED`, `READY_FOR_REVIEW`, `PENDING_TECHNICAL_LEAD_REVIEW` son solo etiquetas de pre-aprobación.
- **Propuestas reales medidas (artifacts V5.5/V5.6 con Fake provider; no existen propuestas de provider real y no se hicieron llamadas):** 2 artifacts, 1 propuesta cada uno (710 y 1951 bytes), 100 % con evidence_refs que resuelven en su índice, 1 de 2 partial/segmentada con request identity, todas `READY_FOR_REVIEW`, 0 canonical. Estado `knowledge/` ausente antes de cualquier decisión.

## 3. Gate B — Diseño mínimo

Paquete nuevo `legacy_documenter/review/` (fuera de `knowledge/` para no alterar el baseline congelado V4-R14 de ese paquete), separado en `models` (contratos/IDs/errores), `evidence` (resolución de refs, solo lectura), `store` (persistencia append-only), `service` (`ApprovalService`) y `render` (vista humana). Adaptador CLI `cli/review_command.py`. Dependencias permitidas: `knowledge.proposals` → `review` → persistencia; el paquete no importa providers, `llm`, `orchestration` ni `cli`.

## 4. HumanDecision y reviewer

Campos: `decision_id`, `proposal_id`, `action` (APPROVE/REJECT/CORRECT/DEFER), `reviewer`, `decided_at`, `rationale`, `correction`, `previous_decision_id`, `proposal_fingerprint`, `evidence_snapshot` + `evidence_fingerprint`, `scope`, `provenance` (método, provider/model, `context_package_id`, request identity). Schema `HUMAN_DECISION 1.0`. `decision_id = DEC-sha256(proposal, action, reviewer, rationale, correction, fingerprints)`; **excluye `decided_at`**, así repetir la misma decisión es idempotente. El reviewer es argumento obligatorio (`--reviewer`, sin fallback a OS/Git/env); se rechaza vacío (`REVIEWER_REQUIRED`) y `AUTO/system/ai/llm/bot/…` o el provider/model de la propuesta (`INVALID_DECISION`).

## 5. Inmutabilidad, stale y tamper

La propuesta es solo lectura. Antes de decidir se recomputa el `PRP-` desde su contenido (mismatch → `PROPOSAL_TAMPERED`), se exige `READY_FOR_REVIEW`, se valida semántica partial (`partial=true`, included/omitted no vacíos y disjuntos, etiqueta de scope en el statement) y se fija un fingerprint de la propuesta completa (incluye metadata); una decisión posterior sobre una propuesta cuyo fingerprint cambió → `PROPOSAL_TAMPERED`. Evidencia: cada ref se resuelve en `index/*.json` y se fingerprintea el registro dueño (`MISSING_EVIDENCE` si no resuelve). `STALE` si (a) el reviewer pasa `--expected-evidence-fingerprint` (mostrado por `review list`) y difiere, o (b) un ref ya snapshotteado en una decisión previa cambió. **Limitación honesta:** los artifacts V5.5/V5.6 no embeben fingerprints de evidencia (no se cambió `AI_PROPOSALS.json` para no alterar outputs), por lo que la línea base de stale es el fingerprint que el humano vio o el snapshot de la primera decisión.

## 6. Semántica de las cuatro acciones

- **APPROVE:** acepta el contenido y materializa canonical (tras grounding/provenance). **REJECT:** persiste decisión; sin canonical; propuesta y evidencia intactas; no es "unresolved". **DEFER:** persiste decisión con rationale; no canonical; la propuesta sigue pendiente y puede revisarse luego (cadena `previous_decision_id`); no es REJECT. **CORRECT:** exige payload humano `{statement, evidence_refs?}` (esquema estricto, sanitizado, tratado como dato); refs agregadas/quitadas se validan contra Evidence y, en segmentos, contra el scope incluido (`INVALID_GROUNDING`); canonical distingue `corrected_from` (propuesta original), contenido humano final y `authored_by = HUMAN_CORRECTION`. Sin correction → `CORRECTION_REQUIRED`; payload malo → `CORRECTION_INVALID`.
- Transiciones: nada → cualquiera; DEFER → cualquiera; APPROVE/REJECT/CORRECT terminales. Misma decisión repetida = no-op idempotente; misma acción terminal por otro reviewer → `DUPLICATE_DECISION`; otra acción → `INVALID_TRANSITION`. No existen APPROVED→PENDING silencioso ni decisión sobre propuesta inexistente (`PROPOSAL_NOT_FOUND`).

## 7. CanonicalKnowledgeRecord, identidad y versionado

Schema `CANONICAL_KNOWLEDGE 1.0`; separado de Evidence y Proposal. Campos: `canonical_id`, `source_proposal_id`, `decision_id`, `decision_action`, `content`, `evidence_refs`, `scope`, `provenance`, `created_at`, `version`=1, `status`=ACTIVE, `supersedes`, `corrected_from`. `canonical_id = CAN-sha256(proposal, decision, contenido final, refs)`; sin UUID/tiempo/provider. Append-only: escritura idéntica = no-op; contenido distinto para el mismo id → `CANONICAL_CONFLICT`/`DUPLICATE_DECISION`; segundo canonical para la misma propuesta → `CANONICAL_CONFLICT`. Un reintento tras fallo entre decision y canonical repara el canonical faltante de forma idempotente. Evidence confidence/status nunca se modifican.

## 8. Partial V5.6, provenance y no-merge

El canonical de un segmento conserva `partial=true`, `parent_flow_id`, `segment_id`, `included_paths`, conteos omitted y `statement_scope=PARTIAL`; la vista humana lo rotula PARTIAL. No hay agregación semántica de segmentos. Provenance canonical: propuesta, decisión, quién/cuándo, refs, provider/model/`context_package_id`/request identity originales, corrección humana, scope, fingerprints de propuesta y evidencia.

## 9. Persistencia, API/CLI y consultas

`<run>/knowledge/decisions/DEC-*.json` y `<run>/knowledge/canonical/CAN-*.json` (JSON determinista, escritura atómica, orden estable, sin secretos ni source crudo) y `knowledge/REVIEW_VIEW.md` (pendientes, decisiones, canonical). Nada de esto existe si ningún humano decide. API Python: `ApprovalService(run_dir, clock).decide(...)`, clock inyectable. CLI: `main.py review list|decide|canonical`; `decide` exige `--output --proposal --action --reviewer` y admite `--rationale --correction-file --expected-evidence-fingerprint`; rechazos salen con exit 4 y código estable. Consultas: list, por `canonical_id`, por `proposal_id`, por `evidence_ref`. Métricas seguras (`reviewed`, conteo por acción, canonical creados), sin rationale/corrección; no se añadieron a RUN_SUMMARY.

## 10. Errores

`PROPOSAL_NOT_FOUND, PROPOSAL_STALE, PROPOSAL_TAMPERED, MISSING_EVIDENCE, INVALID_GROUNDING, INVALID_DECISION, INVALID_TRANSITION, REVIEWER_REQUIRED, CORRECTION_REQUIRED, CORRECTION_INVALID, CANONICAL_CONFLICT, DUPLICATE_DECISION`. Todo falla cerrado antes de escribir. Concurrencia básica: relectura del historial justo antes de escribir (`concurrent_decision_detected`) y rechazo de sobrescritura; sin lock entre procesos (observación).

## 11. Seguridad, cache y fingerprints

Rationale/corrección/reviewer pasan por el sanitizer central + patrones de tokens/headers; control chars neutralizados; contenido nunca ejecutado. No hay prompts, source crudo ni provider en artifacts. `ANALYZER_VERSION=3` y `ANALYZER_CODE_FINGERPRINT=4f7600f0…` sin cambio; decisión/canonical no entran en extraction cache ni en fingerprints; `review_command` se clasificó RUNTIME_ONLY en `CLI_OPTION_CLASSES`.

## 12. Guards arquitectónicos

Tests: ningún módulo de `evidence/`, `knowledge/`, `orchestration/`, `llm/`, `flow_segmentation` ni `full_pipeline` importa `legacy_documenter.review` ni llama `ApprovalService`; el paquete `review` no importa `llm`/Copilot/`orchestration`/`cli`; solo `review_command.py` usa el servicio; `_resolve_provider` no se invoca durante approval; canonical write deja el hash de `index/` y `proposals/` intacto; sin `knowledge/` si nadie revisa.

## 13. Pruebas

- `tests/test_v5_7_r1_human_review.py`: 44 tests (APPROVE/idempotencia/stale/tamper/missing, REJECT, DEFER, CORRECT, transiciones/conflictos, partial, seguridad, determinismo, queries, CLI, guards).
- Dirigidos (V5.7 + V5.6 + V5.5 + hydration/budget + consumer + human docs + proposals + real-provider guard + fingerprints + inventario + baseline V4-R14): **452 tests, 0 failures, 0 errors, 0 skips**.
- Suite completa: **2979 tests, 0 failures, 0 errors, 132 skips** (baseline V5.6: 2935; +44). Se actualizaron los pins del inventario de mantenibilidad (273 módulos; snapshot `V5_7_R1_APPROVAL_CANONICAL_INVENTORY.json`); el paquete se ubicó fuera de `knowledge/` para no modificar el baseline histórico V4-R14.

## 14. Prueba con propuestas reales (copias)

Sobre copias independientes de `proposals/` + `index/` del artifact V5.5 (no segmentado, salida de pipeline real con Fake) y del V5.6 (segmentado): APPROVE, REJECT, CORRECT y DEFER ejecutados en las 8 copias. Resultado: canonical solo en APPROVE/CORRECT (readback exacto); partial preservado en el segmentado; `index/` y `proposals/` byte-idénticos antes/después; artifacts históricos originales intactos; segunda pasada con reloj fijo → árbol `knowledge/` byte-idéntico en las 4 acciones y ambos artifacts. No se aprobó ningún artifact real. 0 llamadas a provider/red.

## 15. Regresión IST sin approval

Una corrida oficial post-cambio (`full`, AI OFF, `long_paths`, cache auto): SUCCESS, `ai_requested=false`, `ai_invoked=false`, real provider calls 0. Comparación contra la salida V5.6: **47523 archivos, 2828066791 bytes, added=0, removed=0, changed=0**. Sin directorios `knowledge/` ni `proposals/` generados. Fuente IST: 15138 archivos, SHA-256 `77965c64…` sin cambios; caches V5.6 y nueva válidas.

## 16. Performance

Validación de propuesta ≈0.5 ms; carga de índice + snapshot en fixture 2.5–3 ms; `decide` completo (validación + persistencia + canonical) ≈20 ms; readback ≈0.7 ms. Sobre el índice real IST (170 020 paths) la carga del `EvidenceIndex` toma ≈8.2 s por operación (observación; aceptable para un acto humano, optimizable con índice lazy en una fase futura). Corrida IST completa 875 s vs 797 s en V5.6 con producción de análisis sin cambios (variación de máquina; extracción fue más rápida: 74 s vs 93 s); no se recalibra.

## 17. Mantenibilidad

Módulos nuevos de 8–242 líneas con responsabilidades separadas; cambios en producción existente mínimos (3 líneas de registro CLI, ruta `review`, 1 clasificación). 0 imports de providers/tecnologías concretas en el paquete; análisis, Evidence Core, adapters y segmentación sin cambios.

## 18. Deuda

- **BLOCKING:** ninguna.
- **FUTURE_PHASE:** UI de revisión, RBAC/autenticación, firma criptográfica, quórum multi-reviewer, bulk approval, merge semántico multi-segmento, grafo/consulta canónica avanzada, API de plugins (V5.8), cross-tech (V5.9), supersede explícito de canonical, lock inter-proceso.
- **OBSERVATION:** stale sin baseline embebido en propuestas V5.5/V5.6 (se apoya en fingerprint visto por el humano/primera decisión); carga de índice ≈8 s en IST real; un `full` posterior elimina `proposals/` pero no `knowledge/` (decisiones huérfanas visibles solo por el store); capas V4-R9/R10 en memoria coexisten sin uso productivo.

## 19. Estado, continuidad y recomendación

`PROJECT_STATE`: `V5.7`, `V5_7_IN_PROGRESS`, completed V5.7-R1, approved V5.6-R3, `V5_7_R1_READY_FOR_HUMAN_REVIEW`, human PENDING, `v5_7_closed=false`, next HUMAN_REVIEW. Roadmaps: estado vigente + ledger; historia preservada. Modelo R1 / R2 solo si defecto / R3, máximo 3 rondas. No se detectó ninguno de los defectos que justifican R2.

**Recomendación: `V5_7_NEXT_R3_FINAL_VERIFICATION`.** Estado final: `V5_7_R1_READY_FOR_HUMAN_REVIEW`. Detenido para revisión humana; V5.8 no iniciada.
