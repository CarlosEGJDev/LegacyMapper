# V5.5 R1 — Integrated Delivery: Generic AI Provider + Context

Estado: `V5_5_R1_READY_FOR_HUMAN_REVIEW`. Revisión humana: PENDING. Recomendación única: `V5_5_NEXT_R3_FINAL_VERIFICATION`. Fecha: 2026-10-07.

## Baseline y fuentes

HEAD=origin/main=`5e9085f0601db4ad68900bbbc523933c51fa5dd3` (V5.4 publicada). Recibo administrativo post-push V5.4 clasificado y conservado byte a byte; prompt R1 aportado por el usuario. AGENTS/CLAUDE/PROJECT_STATE, contratos V5.0 R1/R2A/R3, V5.1, cierres V5.1–V5.4, ambos roadmaps, contratos/cierre/provider históricos V4.3 y código/tests reales inspeccionados antes del diseño; hashes e inventario en JSON. Baseline funcional previa: 138 tests, 0 fallas/errores/skips, 39.192 s, con Fake/clientes simulados.

## Gates A/B: inventario y diseño

127 módulos auditados inicialmente; cinco MIXED: llm/core.py y documentation/{generator,hierarchical,resume,systematic}. Registry por if dentro del contrato; structured_generate fuera del ABC; ausencia de lifecycle; selección/env/modelos y descubrimiento concreto en generadores históricos. Budget, grounding, timeout por llamada y errores por fase existentes reutilizados; no retry de invocación existente. Diseño mínimo: contracts / payload / fake / registry / security / identity / validation; request_budget neutral bajo context. No SDK universal ni plugin discovery.

## Contrato implementado

AIProvider, AIRequest y AIResponse son alias exactos de LLMProvider/LLMRequest/LLMResponse; imports públicos llm y llm.core conservados. ProviderCapabilities añade id/modelo/version a las capacidades heredadas. ABC incluye generate, capabilities, model_info, structured_generate, close idempotente y context manager; context_window/structured_output accesibles como propiedades. Request transporta instrucciones, contexto, provenance/metadata e identidad, output_contract, model_id y timeout_s opcionales. Defaults nuevos no alteran request_id histórico. Response conserva contenido separado de parsed_output, usage, finish/status/error y metadata. Tipos de SDK ausentes del contrato.

## Context selection / packaging / budget

select_flow_ids, AiProjectionBuilder.package, hydration, composer y proposal_adapter AST-idénticos. Política de reserva trasladada a context/request_budget.py con AST equivalente: window menos output declarado (o request menor conocido); window desconocida conserva ceiling de 16000 tokens estimados. Medición incluye instrucciones, políticas, paquete y schema; output_contract embebido usa la misma serialización. Una reducción de perfil; después CONTEXT_TOO_LARGE sin llamada. Conteos incluidos/omitidos, completeness, perfiles/intentos y límite quedan explícitos en métricas; sin segmentación ni listas masivas de continuations. Provider recibe copia aislada del request; refs permitidas calculadas antes de invocar.

## Structured output, provider actual y Fake

structured_output=false produce capability mismatch explícito sin invocar. Soporte lógico no implica JSON schema nativo: fallback del ABC transmite el contrato, parsea JSON localmente y verifica objeto/required; la validación completa de hallazgos/claims y grounding permanece en cada consumidor. Copilot conserva prompt, selección dinámica, permisos/tools desactivados, diagnóstico por fase y cleanup por llamada; model/timeout/output contract neutrales probados con cliente simulado. Sanitización vendor consolidada en llm/security usando el sanitizador central. Fake está separado, sin red: respuesta fija/estructurada, status/error inyectable, ventanas configurables, registro de copias de requests y cierre idempotente. Gemini permanece explícitamente UNREGISTERED; no implementación ni registro nuevo.

## Registry, configuración y secretos

Factories por provider_type, registrables por instancia; built-ins COPILOT y FAKE lazy. Unknown falla; no fallback silencioso. Fake explícito. Resolver disabled devuelve None antes de leer entorno/construir factory. Selección/env trasladadas fuera de orquestación neutral; defaults COPILOT/copilot-local/model auto/2000 output/120 s preservados. Env adicional: LEGACYMAPPER_LLM_TIMEOUT, LEGACYMAPPER_LLM_CONTEXT_WINDOW, LEGACYMAPPER_LLM_MAX_OUTPUT_TOKENS. timeout_s gana sobre options.timeout heredado. Credenciales permanecen exclusivamente en implementación; credential_source es referencia, no valor exportado. Generadores históricos solo cambian su frontera de composición/inyección/lifecycle e identidad de reuse; algoritmos y preflight preservados.

## Error model / lifecycle / retry

Configuration/unavailable/auth/timeout/capability/invalid response/execution/rate limit/cancel se expresan con categorías neutrales; errores y métricas no exportan texto arbitrario de exceptions ni refs desconocidas. Excepciones de resolución conservan categoría de tipo para compatibilidad del guard V4.2-R5.1. Lifecycle cierra en éxito, error, capability mismatch, overflow y contexto ausente; cleanup fallido no oculta el resultado primario y queda registrado. Sin nuevo retry de invocación/jitter; contexto reduce una vez según política aprobada. Exit contract SUCCESS0/PARTIAL1/USAGE2/FAILED4 conservado.

## Grounding y fronteras

Refs de respuesta deben existir en el paquete enviado; malformed/unknown refs y request_id ajeno se rechazan. Provider no modifica Evidence; propuesta conserva origen IA, READY_FOR_REVIEW y PENDING_TECHNICAL_LEAD_REVIEW. Confidence de propuesta nunca sobrescribe state/confirmed/inferred/unresolved de evidencia. Sin aprobación, canonicalización ni generación de hechos desde texto IA. Evidence Core no importa llm; guard AST impide imports concretos desde evidence/context/knowledge/orchestration/documentation. Imports concretos solo en implementaciones, registry/composición y piloto legacy explícito.

## Cache / fingerprints

ANALYZER_VERSION=3, schema evidencia=1.0 y defaults auto/fast/false/None intactos. ANALYZER_CODE_FINGERPRINT=`4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6` sin cambio. Tests mutan fuente de provider/model/config en copia y prueban independencia del fingerprint. Cache V5.4 todavía válida bajo contexto actual; cache V5.5 válida. AICFG separa provider/model/version/capabilities/limits/timeout para outputs IA; request_identity de assessments incluye AICFG. Reuse/migración no acepta identidad antigua/desconocida o configuración distinta; pipeline full siempre regenera proposals. Config IA no entra al fingerprint de análisis.

## Métricas

RUN_SUMMARY conserva contrato/11 claves y determinismo; sin nuevo sidecar canónico. RUN_METRICS agrega ai solo cuando la etapa opt-in se intenta: requested/invoked, provider/model/version, capacidades mínimas, request/success/failure, budget/intentos/omisiones, duraciones de packaging/provider/validación y usage disponible. Vive en _cache_v53 ya excluido contractualmente. IA OFF no agrega claves ni artifacts nuevos. Requests de Fake quedan únicamente en memoria; métricas no contienen instrucciones, records, source, credenciales ni headers.

## Tests y correcciones dentro de R1

57 tests nuevos: contrato/aliases/request id, capabilities, generate-only adapter, JSON fallback, registry explícito/unknown/disabled/custom/duplicado, Fake determinista/structured/error/record isolation, ventanas/reserva/overflow/omisiones, rate limit/cancel sin retry, grounding/inmutabilidad, response identity, seguridad, cache/architecture, provider actual mock y pipeline productivo. Correcciones detectadas y resueltas dentro de R1: schema_included con contrato embebido; preflight antes de composición legacy; categoría RuntimeError del guard histórico; cierre del provider inyectado incluso sin contexto. Sin micro-rondas ni cambios de semántica de análisis upstream. Primera suite: 2906 tests, cuatro fallos de pins históricos (cantidad de módulos, snapshot vivo V5.4, hash y diff de resume.py), cero errores. Se actualizan únicamente los guards afectados al alcance V5.5: inventario vivo separado con comparación completa, nuevo hash estricto de resume.py y guard intacto de deep_source.py; snapshots V4.1/V5.4 conservados. Los 66 controles históricos y 369 caracterizaciones dirigidas pasan antes de repetir la suite completa.

Dirigidos finales: 369 tests, 0 fallas, 0 errores, 0 skips, 60.579 s. Suite exacta requerida: 2907 tests, 0 fallas, 0 errores, 132 skips, 689.446 s, exit0. Skips históricos conservados. Verificación posterior de estado/continuidad: 20 tests, 0 fallas/errores/skips, 1.339 s; auditoría final de inventario, Git, producción congelada y recibo V5.4 PASS. Dependencias/imports y patch targets de tests históricos, y hashes de fuentes obligatorias previas, publicados en inventario JSON. Reader-thread UnicodeDecodeError aparece como diagnóstico histórico no fallido; no se altera producción para corregirlo aquí.

## IST real — IA OFF

Baseline oficial V5.4 reutilizada tras rehacer snapshot de todos sus bytes y cotejarlo con referencia oficial independiente V5.3: 47523 archivos, 2828066791 bytes. Snapshot IST coincide con cierre V5.4: 15138 fuentes, digest `77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5`; antes/después idénticos. UNA corrida post-V5.5, full auto cold / fast / trust-mtime false / ratio None / depth12 / long_paths true / IA OFF. SUCCESS; requested/invoked false; resolución/factory/provider real 0. Source read-only.

Comparador canónico tools/v5_3_compare_full_incremental.py sin cambios: added=0, removed=0, changed=0; 47523 archivos y 2828066791 bytes idénticos. Exclusiones exactas existentes: _cache_v53/ y root RUN_SUMMARY.json, RUN_SUMMARY.md, index/repository.json; ninguna nueva.

## Fake productivo end-to-end

Fixture v4_2_r3_sample: selección → package → contrato genérico → Fake → validación local/grounding → proposal → summary/metrics. SUCCESS; provider v55-r1-fake, model offline-model, 1 request, 1 propuesta grounded; window16000/output2000/input ceiling14000; payload=1649 tokens estimados. Source fixture intacta, provider cerrado; resolución/factory/red real 0; aprobación/canonical false. Artifacts bajo output/_local_v55r1/fake_e2e; detalle en JSON. Generate-only provider independiente atraviesa también interpretación en tests.

## Performance sanity

IA OFF total: V5.4 657.367 s → V5.5 676.784 s (+2.95%). Etapas en tabla. Fake end-to-end 0.941556 s; selección/package 0.00042 s, provider 0.000162 s, validación 5e-06 s. Estimación temporal observacional, no benchmark causal de modelos; sin providers reales ni recalibración. Sanity PASS: variación total menor al 3%, sin cambio de algoritmos deterministas ni outputs; no atribuir causalidad a una sola medición.

| Etapa | V5.4 oficial s | V5.5 oficial s |
| --- | ---: | ---: |
| CONTEXT | 33.872 | 32.901 |
| DOCUMENTATION | 468.503 | 482.978 |
| EXPORT | 63.131 | 59.365 |
| EXTRACTION | 64.018 | 63.142 |

## Maintainability / seguridad / deuda

Scope auditable: 127→135 módulos; MIXED 5→0; módulos con imports concretos 8→4 (todos implementation/composition); imports concretos en fronteras neutrales 0. Shims públicos: llm/core.py e __init__.py; módulos neutrales y módulos >=300 líneas detallados before/after en inventario JSON, sin confundir longitud con complejidad. Algoritmos de evidencia/adapters/extractors/analysis/scanner/models/documentation_v52 conservados; freeze SHA de producción verificado. Frontera real: domain/context → contrato genérico → implementación; los cuatro generadores históricos ya no importan provider/piloto concreto.

BLOCKING: ninguna. FUTURE_PHASE: providers adicionales; retry avanzado/streaming/tools; segmentación V5.6; aprobación V5.7; plugin/discovery V5.8; algoritmos grandes y retirada legacy V5.9+. OBSERVATION: atribución de modelo histórica en consistency_run offline (0 llamadas); manual_verify_full_pipeline usa finding vacío sin refs y puede devolver proceso0 con pipeline PARTIAL; no se modifica ese contrato histórico. Validación productiva Fake de esta ronda utiliza refs de la propia fixture y exige SUCCESS. 0 llamadas reales; sanitizer y fuente read-only preservados; ningún dump de prompts/source/secrets en evidencia R1.

## Estado / continuidad / Git / recomendación

PROJECT_STATE: current_version V5.5, status V5_5_IN_PROGRESS; completed V5.5-R1; approved V5.4-R3; round_status V5_5_R1_READY_FOR_HUMAN_REVIEW; human_review PENDING; next HUMAN_REVIEW; closed false. Contadores históricos globales IA 1/1 intactos; R1 real0 y Fake explícito separado. Cabecera vigente/ledger de ambos roadmaps actualizados; historia y modelo máximo3 rondas preservados.

HEAD/origin/main siguen en cierre V5.4 `5e9085f`; recibo administrativo preservado. Sin commit, push, tag, amend, rebase, reset ni clean. Outputs/logs/harness bajo output/_local_v55r1* ignorados, sin staging. Recomendación única: V5_5_NEXT_R3_FINAL_VERIFICATION tras revisión humana/instrucción; R2 no ejecutada. No iniciar R3 ni V5.6. Ejecución detenida para revisión humana.
