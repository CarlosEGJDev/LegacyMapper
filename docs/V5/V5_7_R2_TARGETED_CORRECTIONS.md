# V5.7 R2 — Targeted Corrections

Fecha: 2026-10-07. Estado: `V5_7_R2_READY_FOR_HUMAN_REVIEW`. Recomendación: `V5_7_NEXT_R3_FINAL_VERIFICATION`.
Evidencia: [JSON](V5_7_R2_TARGETED_CORRECTIONS.json) · inventario: [JSON](V5_7_R2_REVIEW_SNAPSHOT_INVENTORY.json).

Alcance: exactamente dos defectos. Sin rediseño de V5.7 (acciones, reviewer, canonical, append-only, partial, grounding, providers, Evidence Core, segmentación, plantillas) ni inicio de V5.8.

## 1. Defectos confirmados (por inspección del código de R1)

- **A — stale en primera decisión:** en R1, `decide` solo detectaba evidencia cambiada con `--expected-evidence-fingerprint` o con una decisión previa; una primera APPROVE/CORRECT sin esos datos validaba únicamente la evidencia *actual*. Confirmado leyendo la ruta de `decide`; el test de stale de R1 requería un DEFER previo.
- **B — proposal histórico eliminable:** `reset_stale_proposal_artifacts` borra `proposals/AI_PROPOSALS*` al inicio de cada `full`, mientras `knowledge/` permanece, y R1 leía la propuesta solo desde ese artifact: la cadena de auditoría quedaba sin su origen y no se podía continuar una revisión.

## 2. Corrección A — ReviewBaseline

- Nuevo `ReviewBaseline` (`review/baseline.py`): `baseline_id`, `proposal_id`, `proposal_fingerprint`, `evidence_snapshot`, `evidence_fingerprint`, `scope` (incluye metadata partial), `reviewer`, `created_at`. `baseline_id = BAS-sha256(proposal, proposal_fp, evidence_fp)`; sin reviewer ni tiempo en la identidad → preparar el mismo estado dos veces es no-op (se conserva el reviewer/fecha de la primera).
- Nueva operación explícita `ApprovalService.prepare` / `main.py review prepare --output --reviewer [--proposal …]` (por defecto todas las pendientes), persistida en `knowledge/baselines/`. `review list` es de solo lectura y muestra `baseline_prepared`.
- **Regla:** toda primera decisión (APPROVE, REJECT, CORRECT y DEFER) exige baseline; sin él → `BASELINE_REQUIRED` y no se escribe nada (ni siquiera `knowledge/`).
- `decide` recomputa el fingerprint actual de la evidencia de la propuesta y lo compara con el baseline: difiere → `PROPOSAL_STALE`, aunque los refs sigan existiendo. Propuesta distinta → `PROPOSAL_TAMPERED` (separación stale/tampered mantenida). `prepare` sobre evidencia ya cambiada respecto de un baseline existente → `PROPOSAL_STALE` y nunca crea un segundo baseline.
- `--expected-evidence-fingerprint` se mantiene como guard adicional (ya no es la única protección).
- **Recheck optimista:** justo antes de persistir se verifica la firma (tamaño/mtime) de los `index/*.json` cargados; si algo cambió se recarga y recomputa y, si difiere, `PROPOSAL_STALE` sin escribir snapshot, decisión ni canonical. Costo normal: una comparación de `stat`.
- La decisión registra `baseline_id` (campo aditivo; schema `HUMAN_DECISION` 1.0 sin cambio de identidad: `decision_id` no cambia).
- Límite honesto: refs *nuevas* aportadas por una CORRECT humana no existían en el baseline; se validan contra la evidencia actual (existencia y scope) y no contra un estado previo.

## 3. Corrección B — snapshot inmutable de la proposal revisada

- La primera decisión persiste `knowledge/review_snapshots/PRP-….json` (schema `REVIEW_PROPOSAL_SNAPSHOT` 1.0): proposal completo normalizado (metadata, refs, `rationale`, status original), `proposal_id`, `proposal_fingerprint`, scope y metadata partial, provenance (provider/model/`context_package_id`, request identity), `baseline_id` y evidence snapshot/fingerprint. Sin source crudo ni prompts.
- Idempotencia: mismo `proposal_id` + mismo fingerprint → no-op (una sola copia aunque haya DEFER→APPROVE o repeticiones); mismo id con fingerprint distinto → `PROPOSAL_TAMPERED`. Nunca overwrite.
- `full`/limpieza legacy **sin cambios**: limpia `proposals/`; el snapshot permanece. Si el artifact desaparece, `decide`/`prepare` resuelven la propuesta desde el snapshot (verificando que su contenido siga coincidiendo con su fingerprint); si el artifact reaparece distinto del snapshot → `PROPOSAL_TAMPERED`. `review list` y la vista siguen funcionando sin `proposals/`.
- **Cadena de auditoría:** `ReviewStore.audit_chain(decision_id)` y `review canonical --id X --chain` reconstruyen canonical → decision → proposal snapshot → baseline/evidence fingerprint verificando cada eslabón; para REJECT/DEFER: decision → snapshot → baseline. Eslabón faltante → error; fingerprints incoherentes → `PROPOSAL_TAMPERED`.

## 4. Pruebas

- `tests/test_v5_7_r2_review_baseline_and_snapshot.py`: 30 tests — baseline requerido para las 4 acciones, prepare idempotente/reviewer, stale en primer APPROVE/CORRECT/REJECT/DEFER con refs vigentes, no re-baseline, tampered≠stale, expected fingerprint, recheck antes de escribir (race simulado: nada persistido), recheck barato sin cambios, bytes deterministas con reloj fijo, snapshot (creación, readback exacto, 4 acciones, sin duplicados, conflicto, alterado, artifact distinto), partial V5.6 en snapshot, sin secretos, supervivencia a la limpieza de `proposals/`, cadena de auditoría completa y rota, continuar tras limpieza, `index/` intacto, 0 resolución de provider, CLI prepare/decide/`--chain`/list. Los 44 tests de R1 se adaptaron únicamente para llamar a `prepare` antes de decidir.
- Dirigidos (R2, R1, segmentación V5.6, genérico V5.5, proposal integration, real-provider guard, fingerprints/cache, inventario, baseline V4-R14, invariantes de Evidence): **439 tests, 0 failures, 0 errors, 0 skips**.
- Suite completa: **3009 tests, 0 failures, 0 errors, 132 skips** (R1: 2979; +30).

## 5. Pruebas con artifacts reales (copias)

Sobre copias de los artifacts V5.5 (no segmentado) y V5.6 (segmentado): `prepare` → APPROVE/REJECT/CORRECT/DEFER → simulación del cleanup de `full` (`proposals/` eliminado). En las 8 copias: snapshot intacto e idéntico a la propuesta original, historial de decisión intacto, canonical presente solo en APPROVE/CORRECT con readback exacto, cadena de auditoría resuelve, `partial/parent_flow_id/segment_id` conservados en el segmentado, `index/` byte-idéntico, artifacts históricos originales intactos, 0 llamadas a provider. Con reloj fijo, dos pasadas independientes producen el mismo árbol `knowledge/` en las 4 acciones y ambos artifacts.

## 6. Regresión IST sin approval

Una corrida oficial `full` (AI OFF, cache auto): SUCCESS, `ai_requested=false`, `ai_invoked=false`, review no invocado, `knowledge/` y `proposals/` no creados, real provider calls 0. Comparación contra la salida V5.6 (sin exclusiones nuevas): **47523 archivos, 2828066791 bytes, added=0, removed=0, changed=0**. Fuente IST 15138 archivos / SHA-256 `77965c64…` sin cambios; `ANALYZER_VERSION=3` y fingerprint `4f7600f0…` intactos.

## 7. Performance (fixtures)

Crear baseline 11–14 ms; cargar baseline + revalidación stale 3–13 ms; `decide` completo (incl. snapshot) ≈28 ms; readback de snapshot 0.3–0.4 ms. En IST real la carga del índice (≈8 s, observada en R1) se paga una vez por `prepare` y una por `decide`; el recheck previo a escritura no la repite salvo cambio detectado. Corrida IST completa 813 s (V5.7 R1: 875 s; V5.6: 797 s), sin cambio de análisis; no se recalibra.

## 8. Mantenibilidad

`review/baseline.py` (86 líneas) separa los contratos nuevos; `service.py` crece a 318 líneas con responsabilidad única (aplicar decisiones); `store.py` 158; `review_command.py` 97. Sin imports de providers/`llm`/`orchestration`/`cli` en el paquete; sin cambios en pipeline, Evidence Core, segmentación ni limpieza legacy. Pines del inventario actualizados (274 módulos; snapshot R2).

## 9. Deuda

- **RESUELTAS:** first approval sin baseline verificable; proposal revisada eliminable sin snapshot.
- **BLOCKING:** ninguna.
- **FUTURE_PHASE:** lock inter-proceso, UI/RBAC, firmas, quórum, revisión masiva, query avanzada, merge semántico multi-segmento, supersede explícito de canonical.
- **OBSERVATION:** carga de índice ≈8 s en IST real; refs nuevas de una corrección no tienen estado previo; V4 R9/R10 en memoria coexisten sin uso.

## 10. Estado, continuidad y Git

`PROJECT_STATE`: `V5.7`, `V5_7_IN_PROGRESS`, completed V5.7-R2, approved V5.6-R3, `V5_7_R2_READY_FOR_HUMAN_REVIEW`, human PENDING, `v5_7_closed=false`, next HUMAN_REVIEW. Roadmaps: R1 realizada, revisión pidió R2, máximo 3 rondas preservado. Git: sin commit, push, tag, amend, rebase, reset ni clean; base publicada `14280cf8…`, rama `main`, todos los cambios de V5.7 siguen locales. No se crean R2.1/R2.2.

Estado final: `V5_7_R2_READY_FOR_HUMAN_REVIEW`; recomendación `V5_7_NEXT_R3_FINAL_VERIFICATION`. Detenido para revisión humana; V5.8 no iniciada.
