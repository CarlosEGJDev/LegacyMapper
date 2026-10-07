# LegacyMapper V5.6 — R3 Final Verification + Closure + Commit + Push
## Rich Flow Segmentation

## 1. Objetivo

Cerrar V5.6 en una única ronda final.

R1 fue aprobada humanamente y R2 no es necesaria.

Secuencia:

```text
verificación final
→ regresión mínima
→ cierre documental
→ actualización de estado
→ commit único
→ push a origin/main
→ verificación remota
```

NO iniciar V5.7.

## 2. Estado de partida

V5.5 está cerrada y publicada.

Commit base:

`6b8a8138ab6aa90969067fc2b0b63c0671fb07df`

R1 V5.6 aprobada:

```text
V5_6_R1_READY_FOR_HUMAN_REVIEW
V5_6_NEXT_R3_FINAL_VERIFICATION
```

R2:

```text
NOT_REQUIRED
```

Puede existir como modificación administrativa local posterior al push de V5.5:

`docs/V5/V5_5_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Preservarla e incluirla en el cierre si sigue correcta.

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
- iniciar V5.7.

Si el push falla, no usar force, rebase automático ni merge improvisado.

## 4. Fuentes obligatorias

Leer antes de ejecutar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos/cierres V5.0–V5.5
- `docs/V5/V5_6_R1_INTEGRATED_DELIVERY.md`
- `docs/V5/V5_6_R1_INTEGRATED_DELIVERY.json`
- `docs/V5/V5_6_R1_FLOW_SEGMENTATION_INVENTORY.json`
- ambos roadmaps/continuidad
- contratos históricos de hydration/context/budget/proposals relevantes

Regla:

```text
R3 verifica y cierra.
No rediseña V5.6.
```

## 5. Freeze de producción

Antes de validar:

- congelar producción;
- no refactorizar;
- no cambiar segmentation policy;
- no cambiar segment identity;
- no cambiar analyzer version;
- no cambiar provider contracts;
- no introducir persistence/cache nuevo;
- no implementar semantic aggregation;
- no implementar V5.7.

Si aparece un defecto real, corregirlo y repetir las validaciones afectadas.

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
- HEAD en commit base V5.5;
- R1 V5.6 aún sin commit;
- no outputs/cache/IST/temp;
- no secretos;
- no V5.7.

No hacer staging aún.

## 7. Contrato final de segmentación

Revalidar:

```text
AI_SEGMENT_PROJECTION
version = 1.0
```

Campos esperados:

- parent_flow_id;
- segment_id;
- partial;
- ordinal;
- included_paths;
- omitted_paths;
- evidence_refs;
- completeness;
- segmentation_policy;
- segmentation_policy_id;
- segment_reason;
- overlap_paths.

Criterio obligatorio:

```text
segment.partial == true
```

Un segmento nunca puede presentarse como parent completo.

## 8. Policy final

Revalidar:

```text
flow-segmentation-v1
ordering = PATH_ID_ASCENDING
overlap = NONE
oversized = FAIL_EXPLICITLY_NO_FRAGMENTATION
```

No cambiarla durante R3.

## 9. Segment identity

Confirmar determinismo:

```text
SEG-SHA256(parent_flow_id + policy identity + ordered included path IDs + ordinal)
```

No timestamp, random ni provider/model.

## 10. Invariantes

Para cada segmento:

```text
parent existe
partial == true
included_paths != []
omitted_paths != []
included ∩ omitted = ∅
included ∪ omitted = parent paths
evidence_refs ⊆ parent refs válidas
ordinal válido
segment_id reproducible
```

Como overlap = NONE, cada path del parent debe aparecer exactamente una vez entre todos los segments.

## 11. Oversized path

R1 demostró máximo real de 2918 caracteres.

Confirmar:

```text
single oversized path
→ explicit failure
→ no truncation
→ no provider call
```

No implementar intra-path fragmentation.

## 12. Context/Budget integration

Revalidar:

```text
parent flow
→ segmentation if needed
→ segment selection
→ package
→ full request payload gate
→ provider
```

Confirmar:

- budget neutral;
- SMALL unchanged;
- segmented packing respeta ventana neutral;
- TINY fail-closed;
- overflow explícito;
- CONTEXT_TOO_LARGE si tampoco cabe tras segmentar.

## 13. Partial semantics end-to-end

Este es el guard principal de R3.

Verificar que `partial=true` sobreviva:

```text
segment
→ request
→ finding
→ proposal
→ JSON
→ Markdown
→ metrics
```

Debe permanecer visible parent_flow_id, segment_id, completeness/scope e included/omitted counts.

## 14. Grounding

Confirmar:

- provider solo puede referenciar evidencia incluida;
- omitted paths nunca habilitan grounding;
- unknown/malformed refs rechazadas;
- request identity ajena rechazada;
- unresolved preservado;
- confidence no promueve estado;
- provider no muta Evidence.

## 15. No semantic auto-merge

Confirmar que NO existe:

```text
segment 1 AI
+ segment 2 AI
→ automatic complete parent interpretation
```

Solo metadata determinista de cobertura/completitud puede agregarse.

## 16. AI identity

Confirmar que identidad/reuse distingue:

- parent flow;
- segment id;
- segmentation policy id;
- AICFG/provider config.

No mezclar parent completo, distintos segments ni distintas policies.

## 17. Cache/fingerprints

Confirmar:

```text
ANALYZER_VERSION = 3
ANALYZER_CODE_FINGERPRINT = 4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6
Evidence schema = 1.0
```

Criterio:

- extraction cache intacta;
- cambiar segmentation policy no invalida extraction;
- segment/request identity sí cambia;
- no segment cache nueva.

## 18. Human documentation

Confirmar:

- flow completo determinista sigue igual;
- documentación humana no se trocea por defecto;
- propuestas parciales se etiquetan PARTIAL;
- parent/segment visibles.

## 19. Consumer compatibility

Confirmar:

- consumer_projection legacy intacto;
- ai_context persistido legacy intacto;
- consumers existentes no requieren conocer segments;
- nueva forma sigue dedicada al request segmentado/on-demand.

## 20. Persistence

Confirmar:

```text
ON_DEMAND_NO_NEW_CACHE
```

No crear artifact canónico persistido de segments.

## 21. Tests dirigidos R3

Ejecutar como mínimo:

- `tests.test_v5_6_r1_flow_segmentation`
- V5.5 generic AI tests
- hydration/context budget
- consumer projection
- human documentation
- proposal integration
- real-provider guard
- fingerprint/cache
- maintainability/inventory guard

Baseline R1:

```text
378 tests
0 failures
0 errors
0 skips
```

## 22. Suite completa

Ejecutar:

```text
python -X utf8 -m unittest discover -s tests
```

Baseline R1:

```text
2935 tests
0 failures
0 errors
132 skips
```

Criterio:

```text
0 failures
0 errors
```

## 23. Real flow proof

Revalidar:

```text
FLOW-0333008805
341 paths
1512 nodes
826 refs
476066 bytes
85 segments
```

Esperado:

- coverage total;
- no overlap;
- omitted exactos;
- refs subset;
- determinismo byte a byte;
- max payload dentro del gate;
- composition productiva válida.

Revalidar también:

```text
FLOW-0086579093
FLOW-0630348200
```

Deben permanecer sin segmentar.

## 24. IST regression

R1 ya ejecutó una corrida oficial post-cambio:

```text
SUCCESS
AI requested=false
AI invoked=false
real provider calls=0
```

Comparación:

```text
47523 archivos
2828066791 bytes
added=0
removed=0
changed=0
```

R3 no debe repetir una full run si producción está congelada, output R1 íntegro, baseline V5.5 verificable y source IST coincide.

Solo repetir si producción cambia o evidencia deja de ser verificable.

## 25. Source integrity

Esperado:

```text
15138 archivos
SHA256 = 77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5
```

Si cambia, detenerse.

## 26. Fake segmented E2E

Reutilizar evidencia R1 si producción congelada.

Debe demostrar:

```text
large flow
→ segment
→ package
→ Fake
→ grounded finding
→ proposal
```

Esperado:

- request count 1;
- no red;
- parent/SEG presentes;
- partial=true;
- grounding solo included refs;
- omitted explícitos;
- review pending;
- canonical=false;
- provider closed;
- real provider calls=0.

## 27. Performance sanity

R1 real:

```text
0.971773 s
85 segments
1 flow
max payload ~15919 / 16000 estimated tokens
```

No recalibrar. Solo alertar regresión material.

## 28. Maintainability

Revalidar módulos nuevos:

```text
legacy_documenter/context/flow_segmentation.py
legacy_documenter/orchestration/segmented_context.py
```

Criterios:

- 0 concrete provider imports nuevos;
- 0 concrete technology imports nuevos;
- flow resolver sin cambios;
- no dependencia Copilot/WebForms/Oracle;
- responsabilidades separadas.

No confundir la heurística global MIXED con acoplamiento arquitectónico.

## 29. Seguridad

Confirmar:

```text
REAL_PROVIDER_CALLS = 0
REAL_LLM_CALLS = 0
```

Además:

- IST intacto;
- no source crudo;
- no prompts completos;
- no secrets;
- sanitizer intacto;
- output local ignorado;
- no red en Fake.

## 30. Deuda final

Clasificar:

```text
BLOCKING
FUTURE_PHASE
OBSERVATION
```

Esperado no bloqueante:

- semantic multi-segment aggregation;
- cross-flow/adaptive segmentation;
- plugin-facing segment API V5.8;
- segunda tecnología V5.9;
- advanced segment cache;
- omitted IDs consumen budget;
- ventanas pequeñas fail closed;
- una request segmentada no implica interpretación global completa.

No abrir R2 retrospectiva.

## 31. PROJECT_STATE

Si todo pasa:

```text
current_version = V5.6
status = V5_6_CLOSED
latest_completed_round = V5.6-R3
latest_approved_round = V5.6-R1
round_status = CLOSED
human_review = APPROVED
v5_6_closed = true
r2 = NOT_REQUIRED
r3 = COMPLETED
next_version = V5.7
next_round = V5.7-R1
V5_7_READY_TO_START = true
```

No marcar V5.7 iniciada.

## 32. Continuidad

Actualizar únicamente:

- V5.6 R1 approved;
- R2 NOT_REQUIRED;
- R3 completed;
- V5.6 CLOSED;
- V5.7 READY_TO_START.

Preservar historia.

## 33. Documento final

Crear:

`docs/V5/V5_6_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Recomendado:

`docs/V5/V5_6_R3_FINAL_VERIFICATION_AND_CLOSURE.json`

Debe cubrir contrato, policy, identity, invariantes, oversized behavior, budget, partial semantics E2E, grounding, no auto-merge, AI identity, cache/fingerprints, human docs, compatibility, persistence, tests, suite, real flow proof, IST regression, source integrity, Fake E2E, performance, maintainability, security, deuda, estado, continuidad y Git.

## 34. Staging

Antes:

```text
git status --short
git diff --stat
git diff --check
```

Revisar todo.

NO usar `git add .` sin revisión.

Incluir por rutas explícitas:

- producción V5.6;
- tests V5.6;
- docs R1;
- JSON/inventory R1;
- PROJECT_STATE;
- continuidad;
- prompt R1;
- prompt R3;
- informe R3;
- administrativo post-push V5.5 correcto.

Excluir outputs/cache/IST/temp/logs/__pycache__/secrets.

## 35. Commit

Crear UN commit.

Mensaje recomendado:

```text
feat(v5.6): add deterministic flow segmentation
```

No amend.

Registrar hash, parent, stat y archivos.

## 36. Push

Ejecutar:

```text
git push origin main
```

Sin force.

Si falla:

```text
V5_6_R3_PUSH_BLOCKED
```

No alterar historia.

## 37. Verificación remota

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

## 38. Tag

NO crear tag.

Registrar:

```text
TAG_NOT_CREATED_BY_INSTRUCTION
```

## 39. Working tree final

Ideal:

```text
clean
```

Si queda únicamente recibo post-push autorreferencial, documentarlo y no crear segundo commit solo por él.

## 40. Estados finales permitidos

Éxito:

```text
V5_6_CLOSED
V5_6_R3_PUSHED_TO_ORIGIN_MAIN
V5_7_READY_TO_START
```

Bloqueo técnico:

```text
V5_6_R3_BLOCKED
```

Bloqueo solo push:

```text
V5_6_R3_PUSH_BLOCKED
```

## 41. Criterio de cierre

V5.6 queda cerrada si:

- R1 aprobada;
- R2 no requerida;
- segment contract válido;
- identity determinista;
- partial preservado end-to-end;
- omitted explícitos;
- provenance completa;
- no silent truncation;
- grounding limitado al segmento;
- no semantic auto-merge;
- budget neutral correcto;
- extraction cache intacta;
- suite verde;
- regression IST equivalente;
- Fake segmented E2E válido;
- 0 provider calls reales;
- no deuda BLOCKING;
- PROJECT_STATE cerrado;
- continuidad actualizada;
- commit creado;
- push exitoso;
- remoto == HEAD;
- sin tag nuevo;
- V5.7 READY_TO_START pero no iniciada.

Detenerse para revisión humana final.
