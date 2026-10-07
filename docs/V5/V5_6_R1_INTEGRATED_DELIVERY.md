# V5.6 R1 — Integrated Delivery

`V5_6_R1_READY_FOR_HUMAN_REVIEW` · `V5_6_NEXT_R3_FINAL_VERIFICATION`

1. **Objetivo:** flows grandes como proyecciones parciales trazables, sin modificar Evidence Core ni autoaprobar interpretaciones.
2. **Estado inicial:** V5.5 CLOSED/publicada `6b8a8138ab6aa90969067fc2b0b63c0671fb07df`; HEAD=origin/main, main, ahead/behind0/0. Recibo administrativo post-push V5.5 preservado SHA256 `1f71541c1dd05feb16afad49d1f1751905e79768d8048e4732a3ed06a749fe93`; prompt R1 preexistente clasificado.
3. **Fuentes:** AGENTS/CLAUDE/PROJECT_STATE; contratos V5.0 R1/R2A/R3, V5.1 R1/cierre, cierres V5.2–V5.5, V5.5 R1, ambos documentos de continuidad; V4.3 projection/hydration/budget/human/consumer/grounding. Lista completa y SHA iniciales en JSON. Auditoría de analysis/context/evidence/exporters/documentation/documentation_v52/orchestration antes de diseñar.
4. **Baseline IST:** reutilizado `output/_local_v55r1/final`; rehash de 47523 archivos canónicos, 2828066791 bytes, idénticos a referencia retenida. 12642 flows; medición 11.594s, sin reanalizar para medir.
5. **Distribución:** percentiles nearest-rank; bytes JSON canónico UTF-8; tokens estimados ceil(caracteres/4); refs distintas según helper existente. Tabla debajo. 647 records completos superan16000 tokens estimados.
6. **Problema actual:** SMALL individual: 9332 COMPLETE y 3310 BUDGET_INSUFFICIENT/OMITTED; orchestration termina CONTEXT_TOO_LARGE si su ladder no permite paquete. Omite records completos con contadores/continuation; no corta paths internamente. Resolver/composer declaran límites/exclusiones; human hydrata/renderiza flows completos y consumer conserva refs. No se encontró truncación silenciosa de paths en estas vías; truncation=true heredado expresa omisión declarada.
7. **Diseño:** `context/flow_segmentation.py` particiona; `orchestration/segmented_context.py` compone y presupuesta. Path hidratado deduplicado es unidad atómica; mantiene juntos todos sus IDs originales.
8. **Contrato:** `AI_SEGMENT_PROJECTION`1.0 dedicado; parent_flow_id, SEG-id, partial=true boolean, ordinal, included_paths, omitted_paths, evidence_refs, completeness=PARTIAL, segmentation_policy/id, segment_reason, overlap_paths. EvidenceCore/FunctionalFlow no cambian.
9. **Identity:** SEG-SHA256(parent + SEGPOL + IDs incluidos ordenados + ordinal); SEGPOL SHA256 de policy canónica. Sin timestamp/random/provider/model; parámetros numéricos del budget sí son parte de la policy.
10. **Policy:** flow-segmentation-v1, PATH_ID_ASCENDING, greedy con búsqueda binaria, overlapNONE, oversizedFAIL_EXPLICITLY_NO_FRAGMENTATION. Razón PARENT_EXCEEDS_CONSUMER_BUDGET.
11. **Budget:** conserva selección/reducción y bytes de paquetes pequeños. Fallback cuando ladder heredado falla, o selección Python explícita de ordinal. El contrato parcial usa packingLARGE con límite min(160000,input_limit×4); gate final incluye instructions/context/policy/schema y rechaza antes del proveedor. SMALL conserva su umbral original. Los IDs omitidos reales tienen69 caracteres: el segmento mínimo del flow grande mide28608 caracteres; el techo SMALL16000 no puede representar ese contrato. Se conserva la lista completa y se usa la ventana neutral, sin hardcode provider. Perfil explícito TINY (mínimo, sin reducción posible) permanece fail-closed y no se amplía a la ventana de segmentos (preserva V4.3 R5).
12. **Completeness:** PARTIAL explícito en record/request/statistics/proposal; package_completeness distingue packing completo. Parent completo conserva representación heredada (partial ausente equivale a false), sin cambio de schema.
13. **Provenance:** path objects/IDs/refs/confidence originales, path_provenance seleccionado, parent pointers, aggregates recalculados únicamente desde paths incluidos; parámetros/unresolved correspondientes. Extensions del parent conservadas como contexto parent; extensions de paths seleccionados intactas.
14. **Included/omitted:** omitted=parent IDs−included; ambas listas no vacías, disjuntas; union de segmentos=parent, cada ID exactamente una vez. omitted nunca habilita grounding.
15. **Oversized:** máximo path real2918 caracteres; no requiere fragmentación interna. Path indivisible o metadata imposibles abortan todo el plan con código explícito, sin eliminar paths ni invocar provider.
16. **AI context:** una selección parcial por request, primer segmento por defecto; API `run_ai_interpretation(..., segment_ordinal=N)` permite otros. Scope partial/parent/SEG e instrucciones explícitas; contadores para segmentos y flows no enviados. Sin consolidación semántica.
17. **Human docs:** flow completo determinista preservado. Markdown de propuestas parciales añade etiqueta PARTIAL, parent/SEG y counts; listas exactas accesibles en JSON acompañante.
18. **Consumer compatibility:** consumer_projection, ai_context persistido, hidrator y AiProjectionBuilder sin modificaciones. Nueva forma dedicada solo para request segmentado; consumidores heredados siguen iguales.
19. **Persistence:** on-demand, sin nueva cache ni artifact canónico. No persistir source/prompt completo; outputs de prueba locales ignorados.
20. **Cache/fingerprints:** analyzer/extraction SHA `4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6` intacto; ambas caches IST válidas. Test modifica módulo de proyección en copia y demuestra fingerprint estable. Policy modifica solo SEG/request identities.
21. **AI identity:** request contiene parent/SEG/SEGPOL y AICFG; distintos ordinales/configs separados. Finding agrega scope validado en Python; statement de proposal incluye scope para preservar atribución bajo PRP-id heredado. Dominio/identidad canónica no modificados.
22. **Error model:** INVALID_SEGMENTATION_POLICY, INVALID_PARENT_FLOW, INCOMPLETE_PROVENANCE, INVALID_SEGMENT, SINGLE_PATH_OVERSIZED, BUDGET_IMPOSSIBLE_AFTER_SEGMENTATION; SEGMENTATION_NOT_NEEDED para selección explícita sin necesidad. Vía productiva mantiene CONTEXT_TOO_LARGE y failure_category, antes de provider; no provider error fabricado.
23. **Invariantes:** validación reconstruye proyección exacta; rechazo de parent parcial, provenance incompleta/duplicada, tampering, ordinal inválido, partial no boolean. Refs válidas se calculan solo desde paths enviados.
24. **Synthetic proof:** 28 tests nuevos: pequeño, límites exacto/justo sobre, grande, path oversized, shared refs, unresolved, deduplicación atómica, parámetros, extensions, repeat/order/policy, budget imposible, identidad/model, grounding y guard arquitectura neutral.
25. **Real IST proof:** FLOW-0333008805, 341 paths/1512 nodes/826 refs, 476066 bytes →85 segmentos, max35024 bytes por record; union completa, omitted exactos, refs subset, sin overlap. Dos generaciones iguales en bytes canónicos; primer segmento verificado con compositor productivo. FLOW-0086579093 (1 path/1608 bytes) y FLOW-0630348200 (4/4906) no segmentados.
26. **Dirigidos:** 378 tests, 0 failures/errors, 0 skips, 59.14s. Baseline230 PASS, compatibilidad intermedia138 PASS, final segmento/inventory50 PASS. Detalle de módulos y logs locales en JSON.
27. **Suite completa:** `python -X utf8 -m unittest discover -s tests`: 2935 tests, 0 failures, 0 errors, 132 skips explicados heredados; 578.333s. +28 respecto de2907 baseline.
28. **IST regression:** una corrida post-cambio oficial SUCCESS, AI requested=false/invoked=false, provider resolution/registry0. Comparación canónica added0/removed0/changed0, mismas exclusiones heredadas (_cache_v53/, RUN_SUMMARY.json/md, index/repository.json); no nuevas exclusiones. Fuente antes/después SHA idénticos, 15138 archivos. Corrida 796.765s.
29. **Segment artifact determinism:** artifact persistido nuevo N/A; proyecciones on-demand comparadas dos veces byte a byte, sin orphans. Inventario compacto no reemplaza outputs pesados ni constituye nueva evidencia.
30. **Fake segmented E2E:** synthetic hydrated flow→segment→package→Fake→grounded finding→proposal JSON/Markdown; una request, provider cerrado, real resolution0, PENDING_TECHNICAL_LEAD_REVIEW, canonical=false. Parent/SEG/omitted conocidos y scope Python preservado.
31. **Performance:** grande real 0.971773s, 85 segmentos/1 flow; max payload 15919/16000 tokens estimados. Máximo record reducido 92.64%; búsqueda binaria evita probar todos los prefijos crecientes. Listas omitted requieren O(paths×segments) por contrato. No se afirma mejora del pipeline global.
32. **Maintainability:** producción264→266 módulos; dos responsabilidades separadas, imports provider/technology concretos0; flow resolver sin cambios. Inventario antes/después con imports/line count/branches observacionales/riesgo y MIXED heuristic (145→147) en JSON e inventario. Guard histórico apunta al nuevo inventario live; snapshot V5.5 intacto.
33. **Security:** source IST readonly comprobada por hashes; sanitizer central en evidencia exportada/propuestas/reportJSON. Reportes contienen IDs/métricas, sin source crudo ni prompts completos. Fake exclusivo, guard de resolución/registry; real calls0. Contadores globales históricos1/1 preservados.
34. **Debt:** BLOCKING=[]; FUTURE_PHASE=semantic aggregation/cross-flow/adaptive/pluginAPI V5.8/segunda tecnología V5.9/cache avanzada. OBSERVATION=omitted IDs consumen budget; ventanas mínimas fallan explícitamente; selección única no equivale a interpretación completa.
35. **PROJECT_STATE:** V5.6 IN_PROGRESS, completedV5.6-R1, approvedV5.5-R3, round READY_FOR_HUMAN_REVIEW, humanPENDING, nextHUMAN_REVIEW, v5_6_closed=false.
36. **Continuidad:** ambos roadmaps reciben estado vigente y ledgerR1; historia preservada, V5.5 CLOSED, modelo máximo3 rondas y R2 solo si defecto real.
37. **Git:** main, HEAD=origin/main `6b8a8138ab6aa90969067fc2b0b63c0671fb07df`, ahead/behind0/0; sin commit/push/tag/amend/rebase/reset/clean. Cambios exactos registrados en JSON; recibo V5.5 preexistente preservado.
38. **Recomendación:** `V5_6_NEXT_R3_FINAL_VERIFICATION`, únicamente después de revisión/instrucción; R2 no necesaria técnicamente en esta entrega.
39. **Estado final:** `V5_6_R1_READY_FOR_HUMAN_REVIEW`; detención para revisión humana. V5.6 abierta, R3/V5.7 no iniciadas.

| Métrica | p50 | p90 | p95 | p99 | Máximo |
|---|---:|---:|---:|---:|---:|
| raw_paths | 4 | 35 | 58 | 126 | 399 |
| hydrated_paths | 4 | 35 | 58 | 126 | 399 |
| nodes | 8 | 82 | 136 | 306 | 1512 |
| unique_nodes | 5 | 38 | 63 | 128 | 362 |
| evidence_refs | 16 | 124 | 204 | 414 | 1150 |
| bytes | 4902 | 39700 | 64940 | 138696 | 476066 |
| estimated_tokens | 1226 | 9925 | 16235 | 34674 | 119017 |
| max_path_characters | 921 | 1435 | 1487 | 1671 | 2918 |


Evidencia: [JSON](V5_6_R1_INTEGRATED_DELIVERY.json), [inventario](V5_6_R1_FLOW_SEGMENTATION_INVENTORY.json); logs y outputs regenerables ignorados bajo `output/_local_v56r1/`.
