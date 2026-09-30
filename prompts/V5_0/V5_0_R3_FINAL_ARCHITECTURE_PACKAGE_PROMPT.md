# LegacyMapper V5.0 R3 — Final Architecture Package

## Modelo recomendado
Claude Sonnet 5, medium.

## Objetivo
Consolidar la arquitectura final de V5.0 a partir de:
- `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md`
- `docs/V5/V5_0_R2_CONTRACT_VALIDATION.md`
- `docs/V5/V5_0_R2A_CONTRACT_CORRECTIONS.md`

Ronda estrictamente documental. No modificar producción, tests, CLI, providers ni `PROJECT_STATE.json`. No iniciar V5.1.

## Estado de partida
`V5_0_R2A_CONTRACT_CORRECTIONS_READY`

R2A resolvió los conflictos de contrato. Cuando R1 y R2A difieran, R2A prevalece.

## Regla de documentación
Solo crear:
`docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`

No crear prompts siguientes, R3A/R3B, notas de fix, diagnósticos ni otros `.md`.

## Tareas

### 1. Consolidar D-01…D-16
Emitir una matriz final D-01…D-16 sin `CONTRACT_CONFLICT`.

Debe incorporar:
- D-02 Amendment R2A: `EP/EVB/FLOW/DAO/SP/SQL/PATH` preservados; `PAR/CALL/UNRES` solo `legacy_ref`; nuevos `PRJ/CMP/XDP/CAL`; identidad V5 de `UnresolvedBoundary`; `EntryPoint → FunctionalFlow = 1:0..1`.
- D-12 Amendment R2A: `RUN_SUMMARY.json` sin cambios; observabilidad en `RUN_OBSERVABILITY.json`.

### 2. Consolidar Normalized Evidence
Lista final mínima:
`SourceArtifact, Solution, Project, Component, Method/MethodReference, EntryPoint, EventBinding, Call, Instantiation, DataOperation, DataObject, DataParameter, ExternalDependency, FunctionalPath, FunctionalFlow, FlowGraph, UnresolvedBoundary, EvidenceReference, ScanSummary`.

Clasificar cada concepto como:
`core entity | core relation | adapter extension | derived projection | legacy-only field`.

Confirmar que ningún grupo de campos V4.3 queda sin destino.

### 3. Consolidar identidad
Tabla obligatoria:
`Entity | ID prefix | legacy preserved? | canonical V5 identity? | legacy_ref? | natural key | collision rule`

No reintroducir identidades V4.3 inexistentes.

### 4. Consolidar EvidenceReference
Unión final:
`entity | source | source_span | textual` + `legacy_ref?`.

Aclarar:
- proposals usan refs `entity`;
- refs rotas fallan explícitamente;
- no inventar columnas para V4.3.

### 5. Consolidar Projection Contract
Dejar explícito:
`evidence/` = canonical evidence.

`index/` = legacy compatibility projection.

`documentation/` = human presentation.

`ai_context/` = AI-facing projection.

`consumer_projection/` = consumer projection.

`proposals/` = AI proposal output.

### 6. Consolidar Template/Profile/Renderer
Mantener:
`Template = presentación`
`Profile = selección`
`Renderer = formato`

Perfiles mínimos:
`human-functional`, `human-technical`, `ai-context`.

Invariante:
`template_truth_invariance`.

### 7. Consolidar Provider Contract
Resumir contrato final previsto para V5.5:
`generate, structured_generate, capabilities, model_info, close, timeout, rate-limit, retryability, structured output, json mode, context window, max output, sanitization, credential_source, lazy import, registry`.

Provider no toca evidence ni selection.

### 8. Consolidar Runtime/Tooling
Clasificar:
`runtime productivo | tooling desarrollo | legacy congelado`

Incluir `readiness`, `closure`, `human_review`, `second_review` y módulos V3 acoplados a Copilot.

### 9. Consolidar observabilidad
`RUN_SUMMARY.json` permanece compatible V4.3.
`RUN_OBSERVABILITY.json` es sidecar aditivo fuera de D-01.
Clasificar campos required/optional/diagnostic.

### 10. Consolidar incremental/cache future-proofing
Preservar contratos para:
`file fingerprint, adapter version, extractor/stage version, schema version, reverse dependency index, flow invalidation, projection cache key, template/profile version`.

No diseñar algoritmos nuevos.

### 11. Consolidar segmentación
Campos:
`parent_flow_id, segment_id, partial, included_paths, omitted_paths, evidence_refs, segment_reason`.

Invariantes:
- `included ∪ omitted = parent.path_ids`
- `included ∩ omitted = ∅`
- `included ⊆ parent.path_ids`
- `partial=true => omitted != ∅`
- `partial=false => omitted = ∅`

### 12. Consolidar Approval/Canonical
Mantener:
`Evidence → Proposal → HumanDecision → CanonicalKnowledge`

Sin auto-approval ni auto-canonicalization.

### 13. Test baseline decision
Incorporar Opción A como decisión final:
- `PROJECT_STATE.json` es estado/historia acumulada;
- invariantes históricas viven en baseline congelado;
- los 4 tests se corregirán en una ronda separada;
- R3 no modifica tests.

### 14. PRE-V5.1 GATES
Definir explícitamente:
1. aplicar Opción A a los 4 tests;
2. suite completa verde;
3. no editar retroactivamente `PROJECT_STATE.json`;
4. no quedan conflictos contractuales;
5. contrato R1+R2A consolidado;
6. V5.1 implementa sin redefinir identidad/EvidenceReference.

### 15. Alcance exacto V5.1
IN-SCOPE:
- normalized evidence core
- identity implementation
- EvidenceReference
- `evidence/` persistence
- legacy `index/` projection
- collision validation
- schema/version manifest
- adapter reference wrapper
- `RUN_OBSERVABILITY.json` skeleton

OUT-OF-SCOPE:
- template engine completo
- incremental cache
- adapters multi-tecnología
- generic provider implementation
- rich segmentation logic
- approval surface
- plugin runtime

## Output obligatorio
Crear únicamente:
`docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`

Debe contener:
`STATUS, EXECUTIVE SUMMARY, FINAL D-01..D-16 MATRIX, FINAL NORMALIZED EVIDENCE CONTRACT, FINAL IDENTITY CONTRACT, FINAL EVIDENCE REFERENCE CONTRACT, FINAL ADAPTER CONTRACT, FINAL PERSISTENCE/CACHE BOUNDARY, FINAL PROJECTION CONTRACT, FINAL TEMPLATE/PROFILE/RENDERER CONTRACT, FINAL PROVIDER CONTRACT, FINAL RUNTIME/TOOLING BOUNDARY, FINAL OBSERVABILITY CONTRACT, FINAL INCREMENTAL/CACHE FUTURE-PROOFING, FINAL SEGMENTATION CONTRACT, FINAL APPROVAL/CANONICAL BOUNDARY, V4.3→V5 MIGRATION STRATEGY, TEST BASELINE DECISION, PRE-V5.1 GATES, V5.1 IN-SCOPE, V5.1 OUT-OF-SCOPE, RISKS, DEFERRED ITEMS, FILES READ, FILES MODIFIED`.

## Estados permitidos
`V5_0_R3_READY_FOR_PRE_V5_1_GATE`
`V5_0_R3_BLOCKED`

## Restricciones
No modificar producción, tests, CLI, providers, `PROJECT_STATE.json`.
No implementar V5.1.
No ejecutar IA real ni full IST.
No crear archivos auxiliares.
No iniciar V5.1.

## Next step
Si queda `V5_0_R3_READY_FOR_PRE_V5_1_GATE`, no crear ningún prompt siguiente. Esperar aprobación humana.

## Principio
`contrato validado → consolidar → limpiar baseline → implementar una vez`
