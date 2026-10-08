# V5.8 R1 — Integrated Delivery: Consumer / Plugin Contract

Fecha: 2026-10-08. Estado: `V5_8_R1_READY_FOR_HUMAN_REVIEW`. Recomendación: `V5_8_NEXT_R3_FINAL_VERIFICATION`.
Evidencia estructurada: [JSON](V5_8_R1_INTEGRATED_DELIVERY.json) · inventario: [JSON](V5_8_R1_CONSUMER_PLUGIN_INVENTORY.json).

Principio: Core produce proyecciones estables → Consumer Contract define qué se puede leer y pedir → Plugin Contract describe compatibilidad y capacidades → **Plugin Runtime queda fuera** (`Plugin Contract ≠ Plugin Runtime`).

## 1. Objetivo

Formalizar el contrato de consumidores (descriptor, capabilities, request, context, result) y un manifest declarativo de plugins, ambos de solo lectura y verificables, sin cargar ni ejecutar código y sin tocar el análisis, la cache ni los outputs existentes.

## 2. Estado inicial

V5.7 CLOSED y publicada (`bf901dcefcf8c4b100adbe40421e231d2299c7eb`); branch `main`, HEAD = origin/main, ahead/behind 0/0; `v5_8_started=false`, `V5_8_READY_TO_START`. Única modificación previa: recibo post-push de V5.7 en `docs/V5/V5_7_R3_FINAL_VERIFICATION_AND_CLOSURE.md`, preservado sin tocar.

## 3. Fuentes

`AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.json`, `prompts/V5/V5_8_R1_INTEGRATED_DELIVERY.md`, ambos roadmaps; código leído: `context/{consumer_projection,ai_projection,hydration,flow_segmentation}`, `review/*`, `documentation_v52/{engine,writer,defaults}`, `knowledge/{plugin_projection,canonical}`, `evidence/*`, `cli/{router,review_command}`; tests de consumer projection, V5.2, V5.5, V5.6, V5.7, fingerprints y mantenibilidad. Medición antes de diseñar.

## 4. Baseline de consumidores (Gate A)

Inventariados 11 consumidores reales (detalle por consumidor en el inventario JSON: input, output, imports del core, acoplamiento, schema, versionado, capabilities, si muta):

| Consumidor | Clasificación | Migración | Capability |
|---|---|---|---|
| human-functional / human-technical (`documentation_v52`) | ACCEPTABLE | WRAP | `RENDER_HUMAN_DOC` |
| ai-context (`ai_projection`, `ai_context/`) | ACCEPTABLE | WRAP | `READ_AI_CONTEXT` |
| consumer_projection (`LegacyMapperConsumerProjection 1.0`) | ACCEPTABLE | WRAP | `EXPORT_JSON` |
| json exporters (`index/*.json`, `evidence/`) | ACCEPTABLE | KEEP | `READ_EVIDENCE` (vista por id) |
| lectores canonical/review (`review.store`) | MIGRATE_TO_CONTRACT | WRAP | `READ_CANONICAL`, `READ_REVIEW_HISTORY` |
| documentación legacy V3/V4 (`documentation/`) | LEGACY_COMPAT | KEEP | — |
| `knowledge/plugin_projection` (V4-R12, en memoria, sin loader) | LEGACY_COMPAT | DEPRECATE_LATER | — |
| review CLI (única vía que muta, acto humano explícito) | OUT_OF_SCOPE | KEEP | — |
| CLI principal, tests/tools | OUT_OF_SCOPE | KEEP | — |

## 5. Acoplamiento actual (medido)

Módulos de producción (de 282) que nombran el layout `index/`: 24; `ai_context/`: 14; `consumer_projection/`: 8; `documentation_v52/`: 13; `knowledge/`: 15; importan `evidence`: 9, `llm`: 21, `adapters`: 25. En tests: 23 leen `index/`, 26 importan `llm`. Importación dinámica en producción: 2 módulos, ninguno es carga de plugins (`__import__('json')` en `documentation/renderer.py`; `importlib.util.find_spec` como sonda de dependencia opcional en `llm/copilot_pilot.py`). Cargadores de plugins existentes: **0**. Decisión: ningún consumidor histórico se migra; el contrato envuelve las proyecciones estables y la facade es el único lugar nuevo que conoce el layout de un run.

## 6. Diseño

Dos paquetes pequeños, sin abstracciones vacías: `legacy_documenter/consumers/` (`contracts`, `registry`, `sources`, `facade`) y `legacy_documenter/plugins/` (`contracts`, `validation`). Flujo: `Evidence/Core → proyección existente → ConsumerFacade → consumer` y `Plugin Manifest → Contract Validator` (nunca → loader). Cambio mínimo y aditivo en producción existente: `review/store.py` gana lecturas masivas (`baselines`, `chain_of`, `verify_audit_chain`) con la semántica anterior intacta. Sin comando CLI nuevo, sin cambios en `main`/`cli`/pipeline.

## 7. ConsumerDescriptor

`consumer_id, consumer_version, contract_version, capabilities_required, input_kinds, output_kinds, read_only` (todo obligatorio, claves desconocidas rechazadas). `read_only` debe ser `true` (`READ_ONLY_VIOLATION`); capabilities desconocidas → `UNSUPPORTED_CAPABILITY`; kinds fuera del vocabulario → `INVALID_DESCRIPTOR`. Sin configuración de provider ni tecnología.

## 8. Capabilities

Ocho, derivadas del baseline: `READ_EVIDENCE, READ_FLOW, READ_PARTIAL_FLOW, READ_AI_CONTEXT, READ_CANONICAL, READ_REVIEW_HISTORY, RENDER_HUMAN_DOC, EXPORT_JSON`. Una tabla única `CAPABILITY_SPECS` define scopes, límites de entidades, perfiles y opciones permitidas por capability; los descriptors builtin derivan sus kinds de esa tabla. Todo nombre que empieza como mutación (`WRITE_/APPROVE/DECIDE/CREATE_/INVOKE_/EXECUTE/…`) se rechaza como `READ_ONLY_VIOLATION`.

## 9. ConsumerRequest

`consumer_id, contract_version, capability, scope (RUN|ENTITIES), entity_ids, profile, options`. Solo primitivas acotadas (str ≤300, int, bool; ≤8 opciones con claves permitidas por capability); sin objetos, listas anidadas ni callables → no se puede pasar código. `entity_ids` se ordenan y deduplican (mismo request ⇒ misma identidad independientemente del orden).

## 10. ConsumerContext

La facade entrega solo lo que la capability declara y el consumidor tiene concedido. Se preserva evidence refs, provenance, unresolved (los registros se entregan tal cual con su `confidence`/`terminal_type`), semántica partial, provenance canonical y schema/versión. Todo payload pasa por el sanitizer central; no existen prompts, tokens ni credenciales en ninguna capability.

## 11. ConsumerResult

`schema CONSUMER_RESULT`, `contract_name/version`, `result_id`, `consumer_id`, `capability`, `status (OK|ERROR)`, `payload`, `provenance {read_only, provider_calls=0, partial, completeness, source_identities}`, `error {code, detail}`. Errores contractuales con detalle cerrado; excepciones inesperadas salen solo como `INTERNAL_ERROR` con el nombre de la clase, nunca texto ni traceback.

## 12. Plugin Contract vs Runtime

Contract (implementado): identidad, versión, compatibilidad, capabilities requeridas, kinds, permisos declarativos (solo lectura), flags, versión de contrato. Runtime (**no implementado**): discovery dinámico, import/load, sandbox, lifecycle, install/uninstall, aislamiento, resolución de dependencias, firma, ejecución remota. `plugin_runtime = NOT_IMPLEMENTED` en `PROJECT_STATE.json`.

## 13. Plugin manifest

`plugin_id, plugin_version, plugin_contract_version, requires {consumer_contract, capabilities, optional_capabilities}, provides {input_kinds, output_kinds}, read_only, entrypoint_metadata?`. `entrypoint_metadata` es metadata reservada (`kind`, `reference`: texto inerte validado solo en forma y largo); nunca se resuelve, importa ni ejecuta (test con una cadena maliciosa y parches sobre `import_module/exec/eval`).

## 14. Compatibilidad y versionado

Major distinto ⇒ `PLUGIN_INCOMPATIBLE`/`UNSUPPORTED_CONTRACT_VERSION`; minor distinto dentro del mismo major es aditivo y se resuelve a la versión soportada; capability requerida desconocida ⇒ `UNSUPPORTED_CAPABILITY`; opcional desconocida ⇒ se ignora y se informa en `ignored_optional_capabilities`; write-like (requerida u opcional) ⇒ `READ_ONLY_VIOLATION`. Negociación mínima `supported / requested / resolved`, fail closed, sin motor semver.

## 15. Read-only boundary

Contrato read-only por defecto y por construcción: la facade solo lee (`read_text/read_bytes/json`), sin `write*`, `mkdir`, `atomic_write`, `ApprovalService`, `prepare/decide`, cache ni provider (guard AST). Servir las diez variantes de request deja el árbol del run byte-idéntico (hash de árbol antes/después).

## 16. Evidence consumer

`READ_EVIDENCE`: ids de los siete índices primarios resueltos a `{ref, kind, record, record_fingerprint}`; kinds contractuales (`FLOW, PATH, DATA_ACCESS, ENTRY_POINT, SQL_OPERATION, STORED_PROCEDURE, DATA_PARAMETER`); el consumidor no conoce adapters, clases internas ni paths de cache. Id inexistente ⇒ `ENTITY_NOT_FOUND` (fail closed).

## 17. Flow / partial consumer

`READ_FLOW` devuelve el registro hidratado con `partial=false, completeness=COMPLETE`. `READ_PARTIAL_FLOW` llama a `FlowSegmenter` existente y entrega por segmento `partial=true, parent_flow_id, segment_id, included_paths, omitted_paths, evidence_refs` (+ registro); nunca oculta partial (`provenance.partial=true`). Si el flujo cabe o no es segmentable ⇒ `PARTIAL_NOT_SUPPORTED` con el código de segmentación.

## 18. AI-context consumer

`READ_AI_CONTEXT` envuelve `AiProjectionBuilder.build` (perfiles TINY–LARGE; `FULL` rechazado). Budget, segmentación y grounding no se duplican (test: el paquete es idéntico al de `build_ai_projection`). 0 llamadas a provider (`_resolve_provider` parcheado, nunca invocado).

## 19. Human documentation consumer

`RENDER_HUMAN_DOC` con perfiles `human-functional`/`human-technical` ↔ `documentation_v52/general|developer` (mapeo fijado por test contra los perfiles incluidos). `RUN` ⇒ índice paginado + README; `ENTITIES` ⇒ documentos pedidos por ruta, validados contra `MANIFEST.json` (sin rutas construidas por el llamador, sin traversal) y contra su sha256. Profile/Template/Renderer no se tocan.

## 20. Canonical consumer

`READ_CANONICAL` por `canonical_id`, `evidence_ref` o `proposal_id` (o listado `RUN` paginado) a través de `ReviewStore` (lectura), sin exponer archivos internos. Preserva `canonical_id, source_proposal_id, decision_id, decision_action, content, evidence_refs, scope/partial, provenance, version, status, corrected_from`. Sin canonical ⇒ `CANONICAL_NOT_AVAILABLE`; no crea `knowledge/`.

## 21. Review-history consumer

`READ_REVIEW_HISTORY`: decisiones en orden de cadena, baselines, snapshot de la proposal y (opcional) cadena de auditoría verificada. Solo lectura: no existe ruta para APPROVE/REJECT/CORRECT/DEFER (siguen en la Human Review API/CLI explícita).

## 22. Registry / facade

`ConsumerRegistry`: inmutable, ordenado, sin side effects ni imports dinámicos; `with_descriptors` devuelve otro registry; `builtin_registry()` describe los siete consumidores envueltos. `ConsumerFacade(run_dir, registry)`: cachés por instancia (índices, evidencia, manifests), sin estado global. `register_manifests` mapea manifests validados a descriptors (id `plugin.<id>`).

## 23. Errores

`UNKNOWN_CONSUMER, UNSUPPORTED_CONTRACT_VERSION, UNSUPPORTED_CAPABILITY, INVALID_SCOPE, ENTITY_NOT_FOUND, PARTIAL_NOT_SUPPORTED, CANONICAL_NOT_AVAILABLE, INVALID_REQUEST, READ_ONLY_VIOLATION, PLUGIN_MANIFEST_INVALID, PLUGIN_INCOMPATIBLE` (modelo del prompt) + `INVALID_DESCRIPTOR`, `SOURCE_UNAVAILABLE` (artifact ausente/ilegible/hash distinto) e `INTERNAL_ERROR` (solo nombre de clase). Fail closed en todo.

## 24. Determinismo

Mismo request + mismos artifacts + misma versión de contrato ⇒ mismos bytes, orden e identidad (test sobre las diez variantes, entre instancias y con orden de entidades permutado; prueba IST: dos lecturas idénticas). Sin UUID, sin timestamps de la facade. `result_id = CRES-sha256(contrato, consumidor, capability, scope, entidades, perfil, opciones, source identities)`; las source identities son content-derived (fingerprint de registro, `package_id`, ids de decisión/canonical, sha256 de documento), de modo que un cambio en el artifact cambia la identidad.

## 25. Persistencia

On-demand: V5.8 no persiste nada (sin cache nueva, sin manifest/registry en disco). Por tanto no aplican atomic write ni write-if-changed.

## 26. Seguridad

Contrato es datos: nada del manifest, del entrypoint, de un template ni de un comando se ejecuta. Payloads sanitizados con el sanitizer central; sin tokens, credenciales ni prompts; sin source crudo adicional; paths de documentos solo desde manifest verificado.

## 27. Runtime independence

Guards AST: ningún módulo fuera de `consumers/`/`plugins/` los importa (core, evidence, cache, adapters, review, CLI, pipeline); `contracts/registry/plugins` solo importan stdlib y entre sí; la facade importa únicamente `context.{hydration,ai_projection,flow_segmentation}`, `review.{models,store}` y `utils.sanitizer` (sin `llm`, `adapters`, `extractors`, `orchestration`, `cli`, `evidence`, `cache`, `analysis`, `scanner`).

## 28. Compatibilidad / migración

Sin uso de V5.8, el pipeline produce outputs idénticos (IST 0/0/0). Existentes siguen su camino: KEEP/WRAP según §4; nada se deprecó ahora (V4 `plugin_projection` marcado `DEPRECATE_LATER`). Se actualizaron dos pins de tests aprobados: inventario de mantenibilidad (274 → 282 módulos y snapshot nuevo) y el guard de V5.7 «solo el CLI importa el servicio» (ahora además permite que la facade lea `review.store/models`, y verifica explícitamente que `review.service` siga solo en `review_command.py`).

## 29. Tests sintéticos

`tests/test_v5_8_r1_consumer_plugin_contract.py`: **44 tests** — descriptor válido/inválido, registry inmutable, negociación de versión, consumer desconocido, versión no soportada, capability soportada/no concedida/desconocida/de escritura, scope inválido, opciones no primitivas, evidence, flujo completo y parcial (+`segment_id`, +`PARTIAL_NOT_SUPPORTED`), AI-context sin provider, canonical (por id/ref/proposal, partial, no disponible), review history y cadena de auditoría (una sola carga, sin O(N²)), docs human-functional/technical (+hash mismatch, traversal), export, artifacts ausentes, determinismo e identidad, read-only por hash de árbol, redacción de secretos, manifests (aceptado, 15 rechazos, compatibilidad, E2E), guards de arquitectura.

## 30. Fake consumer / plugin

Manifest determinista `fake.docs-summary` con `entrypoint_metadata` hostil: validación → descriptor `plugin.fake.docs-summary` → registry → requests `READ_FLOW`/`READ_EVIDENCE` → `ConsumerResult` OK; `READ_CANONICAL` (no declarada) ⇒ `UNSUPPORTED_CAPABILITY`; capability de escritura ⇒ `READ_ONLY_VIOLATION`; un manifest inválido en el lote ⇒ nada se registra. Sin cargar código ni red.

## 31. Prueba real IST

Sobre la salida IST verificada (V5.7-R2 final, 47523 archivos): evidence lookup (4 kinds), un flujo completo (`FLOW-0000207528`, 1 path), un flujo grande segmentado (`FLOW-0152459726`, 399 paths → **19 segmentos**, todos `partial=true`, unión de `included_paths` = los 399 paths, cada uno con omitted y refs; con el presupuesto por defecto de 16000 caracteres falla cerrado con `PARTIAL_NOT_SUPPORTED: BUDGET_IMPOSSIBLE_AFTER_SEGMENTATION`, comportamiento V5.6 existente), human-functional (5 docs) y human-technical (46561 docs), AI-context SMALL (`AIP-3b74e236…`, 0 provider calls), export manifest (26 particiones), evidencia `unresolved_boundary` preservada. Canonical y review history sobre un artifact local controlado (copia APPROVE del run V5.6 segmentado): 1 canonical `partial=true`, cadena de auditoría verificada; el artifact no cambió. La salida IST no se tocó (mtimes). Solo ids y métricas en este documento.

## 32. Prueba de Plugin Contract

Manifest válido ⇒ aceptado; capability requerida desconocida ⇒ rechazado; contract major incompatible (plugin y consumer) ⇒ rechazado; capability de escritura (requerida u opcional) y `read_only=false` ⇒ rechazados; opcional desconocida ⇒ ignorada e informada. Ningún entrypoint ejecutado.

## 33. Prueba de no-runtime

Guard AST sobre ambos paquetes: sin `importlib/pkgutil/runpy/subprocess/socket/urllib/http/requests/os/shutil/tempfile`, sin `exec/eval/compile/__import__`, sin `walk/scandir/listdir/glob/rglob/iterdir`, sin escritura/borrado, sin `ProviderRegistry/_resolve_provider`. Test adicional enumera los únicos 2 módulos de producción con importación dinámica (no relacionados con plugins) para que no crezcan sin revisión.

## 34. Guards de arquitectura

Evidence/Core → proyección/facade → Consumer Contract → consumer (nada de resolver/provider/adapter arbitrario); Manifest → Validator (nunca Loader); core nunca importa `consumers/`/`plugins/`; `main.py`/`cli/` no exponen comando de consumidor/plugin; `plugins/` no importa facade/sources.

## 35. Cache / fingerprint

`ANALYZER_VERSION = 3` y `ANALYZER_CODE_FINGERPRINT = 4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6` sin cambio (recomputado en test y en la prueba IST); extraction cache no invalidada; los paquetes nuevos están fuera de los directorios del fingerprint.

## 36. Guards de provider y approval

Real provider calls 0 y real LLM calls 0 (tests bajo el guard de `tests/__init__.py`; prueba IST con `_resolve_provider` y `ProviderRegistry.create` parcheados: 0 intentos). La facade y el plugin contract no importan `ApprovalService` ni ninguno de `write_*`/`prepare`/`decide`; un test fija que `legacy_documenter.review.service` sigue importándose solo desde `review_command.py`. Auto-APPROVE/CORRECT, creación de canonical y salto de `ReviewBaseline` quedan estructuralmente imposibles desde el contrato.

## 37. Performance

IST (951 MB de índices): carga de índices 3.5–5.5 s, una vez por facade; construcción del lookup de evidencia 0.6–1.0 s; luego evidence 0.4–0.9 ms, flujo completo 54–97 ms, flujo de 399 paths → 19 segmentos 141–223 ms, AI-context 0.4–0.5 ms, human-functional 48–82 ms, human-technical 8–13 ms, export manifest 0.7–22 ms. Microbenchmark sintético (con la suite corriendo en paralelo): validación de descriptor 4.6 µs, de manifest 8 µs, resolución de capability 12 µs, evidence 15 µs, canonical 0.56 ms. **Defecto propio detectado y corregido en R1:** la primera versión de review-history reescaneaba decisiones/baselines por propuesta (O(N²): 20 propuestas 436 ms, 80 propuestas 6608 ms); ahora carga cada colección una sola vez (20 → 32 ms, 80 → 155 ms) con un test que lo fija. Sin full scan por request: índices, evidencia y manifests se cargan una vez por instancia.

## 38. Mantenibilidad

Antes: 274 módulos de producción; después: 282 (+8: 5 en `consumers/`, 3 en `plugins/`), más 20 líneas aditivas en `review/store.py`. Módulos nuevos de 1–342 líneas (1.016 en total) con responsabilidades separadas (contratos/registry/lectura de artifacts/facade; contratos/validación de manifest); 0 imports de provider/tecnología en las capas puras. Snapshot del inventario regenerado (`V5_8_R1_CONSUMER_PLUGIN_INVENTORY.json`, histórico V4.1 intacto).

## 39. Deuda

- **BLOCKING:** ninguna.
- **FUTURE_PHASE:** plugin runtime dinámico, instalación, sandbox/aislamiento, firma/trust store, registry remoto, permisos/RBAC, hot reload, empaquetado de terceros, ciclo de vida, validación de segunda tecnología (V5.9), capabilities de escritura.
- **OBSERVATION:** la facade asume el layout de un run (`index/`, `documentation_v52/`, `consumer_projection/`, `knowledge/`) como único punto de acoplamiento declarado; la carga de índices IST (≈3.5–5.5 s) es por instancia y a pedido; `knowledge/plugin_projection` (V4-R12) coexiste sin uso productivo; un flujo grande necesita `max_characters` mayor que el default 16000 para segmentarse (comportamiento V5.6).

## 40. Tests dirigidos

`tests.test_v5_8_r1_consumer_plugin_contract` + consumer projection (V4.3-R6) + V5.2 docs/profile/template (7 módulos) + V5.5 generic AI + V5.6 segmentation + V5.7 R1/R2 review/canonical + Evidence core + cache/fingerprint + real-provider guard + mantenibilidad + hidratación, budget y docs humanas V4.3: **727 tests, 0 failures, 0 errors, 0 skips**.

## 41. Suite completa

`python -X utf8 -m unittest discover -s tests`: **3053 tests, 0 failures, 0 errors, 132 skips** en 654.234 s (baseline V5.7: 3009; +44 nuevos).

## 42. Regresión IST

Producción upstream congelada y verificable: el único archivo `.py` rastreado de `legacy_documenter/` modificado es `review/store.py` (helpers de lectura aditivos; solo `review_command.py`, el servicio de review y la facade lo usan, el pipeline no); ninguno de los demás es más nuevo que la corrida oficial IST de V5.7-R2 (comprobado por mtime) y `ANALYZER_CODE_FINGERPRINT` sigue igual. Se reutiliza esa salida tras re-verificarla: **47523 archivos, 2828066791 bytes, added=0, removed=0, changed=0** contra el baseline V5.6; fuente IST **15138 archivos, SHA-256 `77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5`** sin cambios; sin ampliar exclusiones. El pipeline no importa `consumers/`/`plugins/` (guard AST), por lo que «contrato presente pero sin uso» ⇒ outputs legacy iguales.

## 43. PROJECT_STATE

`V5.8`, `V5_8_IN_PROGRESS`, completed `V5.8-R1`, approved `V5.7-R3`, `round_status = V5_8_R1_READY_FOR_HUMAN_REVIEW`, `human_review = PENDING`, `v5_8_closed = false`, `next = HUMAN_REVIEW`, `v5_8_started = true`, `V5_8_READY_TO_START = false`, `plugin_runtime = NOT_IMPLEMENTED`, bloque `v5_8_contract`. V5.8 no marcada cerrada.

## 44. Continuidad

Ambos roadmaps: V5.7 CLOSED, V5.8 R1, Plugin Contract separado de Plugin Runtime, R2 solo por defecto real, V5.9 no iniciada; historia preservada.

## 45. Git

Solo consultas. Branch `main`; HEAD = origin/main = `bf901dcefcf8c4b100adbe40421e231d2299c7eb`; ahead/behind 0/0. Cambios locales: `PROJECT_STATE.json`, `legacy_documenter/review/store.py`, `tests/test_v4_1_r0_maintainability_inventory.py`, `tests/test_v5_7_r1_human_review.py`, ambos roadmaps, recibo post-push V5.7 (preservado); nuevos: `legacy_documenter/consumers/` (5), `legacy_documenter/plugins/` (3), `tests/test_v5_8_r1_consumer_plugin_contract.py`, `docs/V5/V5_8_R1_*`, `prompts/V5/V5_8_R1_INTEGRATED_DELIVERY.md`. Recibo post-push V5.7 ya presente. Sin commit, push, tag, amend, rebase, reset ni clean.

## 46. Recomendación R2/R3

Ningún defecto que justifique R2: sin dependencia de internals críticos por parte de la facade fuera de su único seam declarado, partial preservado, el plugin contract no ejecuta código, sin capability de escritura aceptada, review/canonical no mutables, sin acoplamiento a provider/tecnología, versiones incompatibles rechazadas, sin regresión IST, suite verde. El defecto de rendimiento de review-history se encontró y corrigió dentro de R1.

**Recomendación: `V5_8_NEXT_R3_FINAL_VERIFICATION`.**

## 47. Estado final

`V5_8_R1_READY_FOR_HUMAN_REVIEW`. Detenido para revisión humana; Plugin Runtime no implementado; providers reales no activados; V5.9 no iniciada.
