# V5 Closure R1 — Final Audit & Release Baseline

Fecha: 2026-10-09. Estado: **`V5_CLOSURE_R1_READY_FOR_HUMAN_REVIEW`**. Recomendación: **`V5_CLOSURE_NEXT_R3_FINAL_CLOSURE`**.
Auditoría, no desarrollo: **producción sin cambios**, sin commit/push/tag, sin provider real, sin capability nueva. Evidencia máquina-legible: [V5_FINAL_BASELINE.json](V5_FINAL_BASELINE.json), [V5_CLOSURE_R1_RESULT.json](V5_CLOSURE_R1_RESULT.json), [matriz de contratos](V5_FINAL_CONTRACT_MATRIX.json), [matriz de invariantes](V5_FINAL_INVARIANT_MATRIX.json), [deuda consolidada](V5_FINAL_DEBT_LEDGER.json), [inventario de mantenibilidad](V5_FINAL_MAINTAINABILITY_INVENTORY.json), [guía operativa](V5_OPERATIONS_GUIDE.md).

**Pregunta central:** ¿V5 cumple su objetivo global sin romper IST y con fronteras suficientes para evolucionar a múltiples tecnologías, providers, consumidores y conocimiento canónico? **Sí**, con deuda no bloqueante documentada (§16). No es solo «tests verdes»: se midió el grafo de dependencias, se verificaron constantes de contrato contra el código, se re-verificó IST y se volvió a ejecutar el piloto Python.

## 1. Objetivo global de V5

Roadmap oficial: «Python descubre, estructura, selecciona y valida; la IA interpreta». Orden V5.0 Architecture & Contracts → V5.1 Normalized Evidence → V5.2 Templates/Profiles → V5.3 Incremental/Cache → V5.4 Adapters → V5.5 AI Provider/Context → V5.6 Segmentation → V5.7 Approval/Canonical → V5.8 Consumer/Plugin Contract → V5.9 Multi-technology pilot → Closure.

## 2. Qué cambió desde V4.3

V4.3 cerró documentación y proyecciones para IST con un pipeline acoplado a VB.NET/WebForms/Oracle. V5 separó esa tecnología del core (adapters), introdujo un Evidence neutral con ids deterministas y provenance fail-closed, documentación por perfiles/templates, cache incremental con fingerprints, un contrato de provider genérico, segmentación sin truncación silenciosa, gobierno humano de la IA (propuesta → decisión → canónico), contratos de consumidores/plugins de solo lectura y una segunda tecnología real (Python) con identidad de repositorio.

## 3. Arquitectura final (medida)

```text
Evidence/Core ← Adapters (vbnet-webforms-oracle, python-generic; composition root = cli/pipeline_stages)
Evidence → Documentation (documentation_v52: profiles/templates/renderer)  → Cache/Incremental (fingerprints)
Evidence → Context (hydration, ai_projection, segmentation) → Provider (llm) → Proposal (pendiente)
Proposal → Review (humano) → Canonical      Consumers/Plugins (read-only, facade) ← artifacts
```

Hechos verificados por AST sobre los 290 módulos de producción: (a) el runtime no abre rutas `docs/`, `prompts/`, `tests/` ni importa `tests`/`tools`; (b) importar `cache/evidence/review/consumers/plugins/context` no carga ningún módulo de provider; (c) solo los dos shims V5.4 (`evidence/builder.py`, `evidence/projection.py`) importan un adapter desde una capa neutral — documentados y protegidos por test; (d) `consumers` y `plugins` quedan **fuera** del clúster de importación histórico y `adapters/python_generic` solo importa `analysis`, `evidence`, `models` y `utils` (aristas que `adapters` ya tenía); (e) `ApprovalService` solo lo importa `cli/review_command.py`; (f) 0 `except` desnudos, 42 `except Exception` en fronteras de etapa; (g) 1 `__import__('json')` benigno y 1 sonda `importlib.util.find_spec` de dependencia opcional (ninguno carga plugins).

**Hallazgo (no bloqueante, OB-11):** existe un clúster de 14 paquetes con importaciones mutuas (adapters, analysis, cache, cli, documentation, documentation_v52, evidence, exporters, fingerprints, knowledge, llm, main, orchestration, review). Se midió en cinco commits: ya existía antes de V5.4 (commit `9425319`) con 11 paquetes; V5.4 sumó `adapters` y `evidence` (por los shims de compatibilidad) y V5.7 sumó `review` (por `documentation.contracts.stable_id`); **V5.8 y V5.9 no añadieron ningún ciclo**. Es deuda de modularidad histórica, no una contradicción de contrato. **Hallazgo OB-12:** `cache/run_metrics` importa un helper de `llm.security` (perezoso; no carga providers).

## 4. Resumen V5.0–V5.9

| Versión | Entrega | Cierre |
|---|---|---|
| V5.0 | Contratos de arquitectura (core, adapters, proyección, templates, provider) | CLOSED (`V5_0_R3`, formalizado en `V5_2_R4_3`) |
| V5.1 | Normalized Evidence Core (schema 1.0, 13 tipos de identidad, I-1…I-11) | CLOSED (`V5_1_R4`) |
| V5.2 | `documentation_v52` (perfiles `general`=human-functional, `developer`=human-technical; `ai_context`) | CLOSED, `6c32c4c`, tag `v5.2` |
| V5.3 | Cache de extracción, fingerprints, scope, métricas | CLOSED, `9425319` |
| V5.4 | Separación tecnología/adapters; `vbnet-webforms-oracle` 1.0 | CLOSED, `5e9085f` |
| V5.5 | Contrato de provider genérico, Fake networkless, budgets | CLOSED, `6b8a813` |
| V5.6 | Segmentación de flujos con provenance | CLOSED, `14280cf` |
| V5.7 | Review humano, baseline, snapshot, canónico, audit chain | CLOSED, `bf901dc` |
| V5.8 | Consumer Contract 1.0 + Plugin Contract 1.0 (≠ Runtime) | CLOSED, `bcb8d57` |
| V5.9 | `python-generic` 1.0, piloto circular, namespace de `SourceArtifact` | CLOSED, `957ef09` |

## 5. Matriz de contratos

Ver [V5_FINAL_CONTRACT_MATRIX.json](V5_FINAL_CONTRACT_MATRIX.json) (construida leyendo las constantes del código y comprobando la existencia de cada ruta). Versiones explícitas verificadas: `ANALYZER_VERSION=3`, `EVIDENCE_SCHEMA_VERSION=1.0`, `LegacyMapperConsumerContract 1.0` (8 capabilities), `LegacyMapperPluginContract 1.0`, `AI_HYDRATED_PROJECTION 1.0`, `LegacyMapperConsumerProjection 1.0`, hidratación `V4.3-R3`, segmentación `flow-segmentation-v1`, `HUMAN_DECISION`/`CANONICAL_KNOWLEDGE`/`REVIEW_BASELINE` 1.0, extraction cache schema 1, manifest `LegacyMapperDocumentationV52`, adapters `vbnet-webforms-oracle` 1.0 y `python-generic` 1.0.

## 6. Matriz de invariantes

Ver [V5_FINAL_INVARIANT_MATRIX.json](V5_FINAL_INVARIANT_MATRIX.json): las 14 invariantes pedidas (determinismo, provenance, unresolved, compatibilidad IST, independencia de runtime, neutralidad de provider y de tecnología, sin auto-aprobación ni auto-canonicalización, parcialidad explícita, consumers de solo lectura, sin Plugin Runtime, sin mutación de fuente, sin provider real en el pipeline determinista) quedan **HELD**; la de independencia de runtime «HELD_WITH_HISTORICAL_COMPAT» por los shims y el clúster histórico.

## 7. Baseline IST

Fuente: **15 138 archivos, SHA-256 `77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5`**. Salida: **47 523 archivos, 2 828 066 791 bytes, added=0, removed=0, changed=0**. `ANALYZER_VERSION=3`, `ANALYZER_CODE_FINGERPRINT=f05b2de43b726e75e03b97e1d35fef8b3407d54247e0a4e4537ab24d282fa26b`. Se reutilizó la corrida completa de V5.9-R2 porque producción sigue congelada (árbol de trabajo limpio en `legacy_documenter/` respecto de `957ef09`, nada modificado desde que empezó la corrida), el fingerprint coincide con el de la corrida y la fuente coincide; **se volvió a verificar** fuente y salida (snapshot de 47 523 archivos contra la referencia) en esta ronda. Corrida real de referencia: 651.7 s cold, pico ≈3.0 GB (V5.4: 657 s; V5.5: 677 s).

## 8. Baseline del piloto Python

`pilot_kind=SELF_HOSTED_CIRCULAR`, `real_second_technology=true`, `second_source_is_legacy_mapper_itself=true`, **`external_independence_claim=false`**, `independent_external_product=false` (no se convierte en un claim externo). `SECOND_TECH_SOURCE_ID=SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60`, origen `e9e3d606…`, tree hash `a190898bd89683a8ae443fd9d0640e37fc454327ceea34cacdd818c2862ce39e` (intacto tras todas las corridas), `python-generic` 1.0, `repository_id` declarado. Conteos: SourceArtifact 540, Project 4, Component 887, EntryPoint 73, Call 16 145, ExternalDependency 1, DataOperation 692, FunctionalFlow 19, FunctionalPath 4 600, UnresolvedBoundary 4 191, EvidenceReference 22 514. IDs compartidos IST/Python (con id declarado): **total_shared_ids = 0**; relocación a otro root: mismos `SRC-` y particiones idénticas salvo las que imprimen el root físico (7 de 4 640 archivos).

## 9. Tests

- **Cierre dirigido:** `python -X utf8 -m unittest` sobre 28 módulos (evidence, documentación, cache/fingerprints/scope, adapters, provider guard, segmentación, review/canónico, consumers/plugins, identidad V5.9-R2, independencia de runtime, mantenibilidad, regresión/seguridad V4): **970 tests, 0 failures, 0 errors** (306 s).
- **Suite completa** `python -X utf8 -m unittest discover -s tests`: **3 100 tests, 0 failures, 0 errors, 132 skips** (668.1 s) = baseline. Los 132 skips son los esperados de checkout limpio (artefactos locales ausentes).

## 10. Performance

IST cold ≈652 s (extracción 69 s, flujos 6.6 s, export/evidence 82 s, documentación 446 s). Python (243 archivos): cold 42–57 s, warm 6 s (243 hits), incremental 7–8 s. Consumers: carga de índices IST 3.4–5.5 s por instancia, lecturas en milisegundos. Sin regresión material entre V5.4 y V5.9.

## 11. Determinismo

Dos corridas cold del corpus Python en directorios distintos: 4 640 archivos idénticos (0/0/0); warm idéntico al cold; incremental idéntico al cold de la copia mutada (1 archivo cambiado: 242 hits / 1 miss / 1 re-extraído; 17 archivos de salida cambiados + 1 añadido); lecturas repetidas de los consumers idénticas en bytes; el fingerprint del analyzer entra a toda clave de cache, de modo que una cache incompatible no se reutiliza. La identidad física de la cache (ruta raíz) y la identidad lógica del repositorio (`repository_id`) permanecen separadas. Limitación conocida, no reabierta: el scope incremental puede reportar `mode=full` para cambios de código (resolución global conservadora).

## 12. Seguridad

Sin secretos versionados (1 coincidencia de patrón = un centinela de prueba `password=` en un test de saneado; 0 en producción); sin ejecución del target (solo `ast.parse`), sin red accidental (únicos imports de red: el provider Gemini no registrado y la sonda de dependencia), 0 llamadas a provider real (guard parcheado nunca invocado en las corridas de cierre), sin carga dinámica de plugins, ids sin rutas absolutas ni datos de máquina, guards de traversal y de hash en la lectura de documentos, sanitizer central en toda salida de consumers, fuente de solo lectura. 117 artefactos pequeños bajo `output/` están versionados por política documentada. No se hizo pentest general.

## 13. Gobierno de review / canonical

`APPROVE | REJECT | CORRECT | DEFER` con revisor explícito (rechaza `AUTO`, `system`, `ai`, `llm`, provider y modelo de la propuesta); sin AUTO_APPROVE ni AI_APPROVE en el vocabulario; `prepare` fija baseline; evidencia alterada → `PROPOSAL_STALE`; propuesta alterada → `PROPOSAL_TAMPERED`; snapshot inmutable que sobrevive a limpiezas; canónico solo desde APPROVE/CORRECT; cadena canónico → decisión → snapshot → baseline → evidencia; procedencia parcial conservada. **Precisión contractual:** el baseline prueba estabilidad **entre `review prepare` y la decisión**; las propuestas no llevan huella de evidencia al generarse (verificado en el código), así que no se afirma inmutabilidad desde la generación. Re-verificado en la copia Python: APPROVE → canónico con readback igual y cadena válida; mutación posterior → `PROPOSAL_STALE`; el artifact original queda sin `knowledge/`.

## 14. Frontera consumer / plugin

Contrato 1.0 con 8 capabilities de solo lectura (servidas sobre IST y Python); `READ_PARTIAL_FLOW` real: `FLOW-0042743202` → 108 segmentos con unión = padre, sin solape. `Plugin Contract ≠ Plugin Runtime`: el manifest Fake V5.8 da `READ_EVIDENCE`/`READ_FLOW` OK, capability no declarada → `UNSUPPORTED_CAPABILITY`, escritura → `READ_ONLY_VIOLATION`; sin loaders, instalación, descubrimiento, sandbox ni hot reload. Plugin Runtime queda fuera de V5.

## 15. Limitaciones

El piloto Python es circular (§8); resolución estática sin inferencia de tipos (≈42 % de llamadas Python sin resolver, por diseño); entry points Python solo por `__main__`; repositorios sin `--repository-id` comparten el espacio de ids V5.1 (observación, no se cambió); `PRJ-/CMP-/CAL-/XDP-` derivan de rutas; algunas salidas de presentación imprimen el nombre del directorio raíz; documentos de orientación (`README.md`, `docs/PROJECT_RECOVERY.md`, lista de lectura de `CLAUDE.md`) siguen apuntando a material V4 (los comandos siguen siendo válidos; la guía V5 nueva los complementa).

## 16. Deuda consolidada

Ver [V5_FINAL_DEBT_LEDGER.json](V5_FINAL_DEBT_LEDGER.json) (deduplicada V5.0–V5.9, con id, versión de origen, clasificación, estado, evidencia y fase recomendada): **BLOCKING 0 · FUTURE_PHASE 14 · OBSERVATION 15 · HISTORICAL_COMPATIBILITY 5**. Las 10 deudas esperadas por el prompt se revisaron una a una y siguen vigentes (validación externa independiente, inferencia de tipos Python, argparse/console, adapters DB Python, Plugin Runtime, tercera tecnología, namespace de repos no declarados, ids derivados de rutas, nombres del root en presentación, scope incremental conservador). Hallazgos nuevos de la auditoría, todos no bloqueantes: clúster de importación histórico (OB-11), `cache → llm.security` (OB-12), 42 handlers `except Exception` (OB-13), documentos de orientación desactualizados (OB-14).

## 17. Guía operativa

[V5_OPERATIONS_GUIDE.md](V5_OPERATIONS_GUIDE.md): comandos reales (`analyze`, `full`, `review list|prepare|decide|canonical`, `readiness`, `output-manifest`; **no existe CLI de consumers**), IST/Python, `--repository-id`, cache/incremental, activación segura de la IA, review/canónico, consumers, qué es y qué no es el Plugin Contract, y qué NO está implementado. Separa evidencia determinista, propuesta de IA, aprobación humana y conocimiento canónico. Los comandos y opciones se copiaron de `--help`, no se inventaron.

## 18. Rollback y compatibilidad

Cada versión tiene su commit (§4); solo `v5.2` tiene tag (el resto: `TAG_NOT_CREATED_BY_INSTRUCTION`). Sin `--repository-id` los ids y las salidas de IST son los de V5.1 (probado byte a byte); declararlo es opt-in y no migra baselines. El fingerprint del analyzer cambió en V5.9 (`4f7600f0…` → `ce21000d…` → `f05b2de4…`): las caches de extracción previas se invalidan una vez y se reconstruyen solas; `ANALYZER_VERSION` sigue en 3. Los shims y la estructura `index/`/`documentation/` heredados se conservan, de modo que consumidores V4 siguen funcionando.

## 19. Release readiness

Auditoría limpia: sin contradicción de contrato, sin invariante rota, sin regresión IST, sin fallo de suite, sin provenance rota, sin fuga arquitectónica nueva bloqueante, sin ejecución de provider real, sin auto-aprobación/canonicalización, consumers de solo lectura, identidad multi-tecnología correcta, sin bloqueo de seguridad y sin documentación de comandos materialmente incorrecta. Candidato a commit de producción V5: `957ef09538a7afea649d1f2ac195a3d3819a660f` (HEAD = origin/main, 0/0). El árbol de trabajo solo contiene el recibo post-push de V5.9 (preservado), esta ronda y su prompt. Pendiente para el cierre: decisión humana sobre commit/push/tag de cierre (no autorizados en R1).

## 20. Recomendación

Ningún criterio de R2 se cumple (§38 del prompt); no se abre por refactors, estilo, adapters futuros, tercera tecnología, Plugin Runtime, corpus externo ni mejoras de inferencia. **`V5_CLOSURE_NEXT_R3_FINAL_CLOSURE`.** Estado final: `V5_CLOSURE_R1_READY_FOR_HUMAN_REVIEW`; detenido para revisión humana; V5 **no** marcado como cerrado; sin V6.
