# V5.4 R1 — Integrated Delivery

## 1. Objetivo
Separación real Technology/DB Adapter → evidencia/recorridos neutrales → proyecciones existentes. Resultado: `V5_4_R1_READY_FOR_HUMAN_REVIEW`.

## 2. Estado inicial
V5.3 cerrada y publicada; main, HEAD y origin/main = `9425319cb2edbae896b96f7abfbdcd3764beb538`; ahead/behind 0/0; sin tag v5.3. Administrativos R4.1 existentes preservados. V5.4 iniciada únicamente por el prompt activo.

## 3. Fuentes/contratos leídos
AGENTS.md; CLAUDE.md; PROJECT_STATE.json; V5_0_R1_ARCHITECTURE_CONTRACT, V5_0_R2A_CONTRACT_CORRECTIONS, V5_0_R3_FINAL_ARCHITECTURE_PACKAGE; V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT; V5_1_R4_CIERRE_FINAL; V5_2_R4_3_CIERRE_FORMAL; V5_3_R4_CLOSURE; ambos documentos de continuidad/roadmap. Fronteras finales V5.0 prevalecen: el recorrido consume hechos neutrales. La compatibilidad legacy permitida por V5.1 permanece como proyección del adapter. Sin contradicción contractual identificada.

## 4. Baseline de acoplamientos
Inventario AST previo: 62 módulos relevantes; 15 módulos de tests importaban extractores/resolvers directamente. Incluye extractors, analysis, models, evidence, cli, scanner, fingerprints. No existe implementación pipeline adicional fuera de cli/pipeline_stages y cli/full_pipeline. Clasificaciones completas, imports, APIs públicas y conteos textuales en JSON acompañante.

Material: invariants y persistence importaban builder MIXED; flow_resolver MIXED combinaba etiquetas WebForms/casefold VB con recorrido genérico. Builder/projection y flow = 3 fronteras mixtas. Helpers DB y database_resolver eran específicos de VB/ADO.NET/Oracle. Clasificación previa: `{"TECHNOLOGY_ADAPTER": 12, "DB-SPECIFIC CAPABILITY": 5, "CORE": 16, "LEGACY COMPATIBILITY / DIAGNOSTIC COMPOSITION": 3, "MIXED": 3, "LEGACY COMPATIBILITY": 9, "COMPOSITION/ORCHESTRATION": 14}`. Conteos textuales incluyen rutas de import/shims y comentarios: pueden crecer al introducir el nombre explícito del adapter; no miden por sí solos acoplamiento material.

## 5. Decisión de arquitectura
Opción A: adapter compuesto `vbnet-webforms-oracle` 1.0, capabilities internas. El parsing/resolución DB depende del contexto de métodos/tokens VB; separarlo como provider DB público introduciría una interfaz sin segundo consumidor real. No se crean tecnologías futuras ni framework/plugin runtime.

## 6. Contrato de adapter
AdapterCapabilities inmutable: identidad/version, source_kinds, capabilities, schema target 1.0. TechnologyAdapter protocol mínimo; AdapterRegistry explícito. Selección por intersección de tipos de archivos observados; candidatos ordenados por ID, sin prioridad implícita. Duplicado/descriptor inválido/ambigüedad → AdapterSelectionError; ningún candidato → None. Pipeline rechaza repositorio no vacío no soportado con UNSUPPORTED_TECHNOLOGY; repositorio vacío usa referencia sin inventar hechos.

## 7. DB boundary
DatabaseExtractor, 3 helpers y DatabaseResolver canónicos bajo adapter. Stored procedures, SQL, parámetros, transacciones, conexiones y targets unresolved conservan algoritmos y evidencia. Normalización emite DataOperation/DataObject/DataParameter/ExternalDependency; datos específicos conservados bajo extensions[adapter_id] y provenance. Sin promoción de unresolved.

## 8. Archivos cambiados
33 módulos de producción nuevos: 28 bajo adapters/, bundle.py y 4 módulos de recorrido neutral. 21 módulos anteriores se convierten en reexports puros. Pipeline: extracción/resolución/normalización por referencia compuesta; cache.context, fingerprints.code y versions actualizados. Tests: nuevo test_v5_4_r1_adapters; guardianes de fingerprint e inventario actualizados. Estado/continuidad y 3 artefactos de resultado bajo docs/V5. Inventario exacto de modificaciones/nuevos en JSON `git.status`.

## 9. Migración/compatibilidad
Imports anteriores de extractores/resolvers/builder/projector preservan identidad de clases. Patches históricos siguen llegando a clases canónicas. Extracción conserva orden, namespaces, partial handling y registros de caché. Builder conserva AST completo; 16 módulos algorítmicos y 2 helpers genéricos conservan cuerpos AST, además de 20 métodos de recorrido (incluido _walk). Preparación de claves/etiquetas y remapeo de campos legacy quedan en adapter; núcleo recorre únicamente hechos preparados. Ningún shim añade lógica. Rollback requiere restaurar código/analyzer 2 y reconstruir caché; nunca aceptar caché cruzada por versión.

## 10. Adapter WebForms/VB.NET/Oracle
Tipos soportados: solution, vb_project, vb_source, aspx, ascx, master, web_config. Capabilities: extracción, calls, entries, dependencies, database, normalized_evidence. Mantiene IDs históricos y outputs legacy/V5.1/V5.2; composición CLI preservada.

## 11. Fake adapter proof
SyntheticAdapter exclusivo de tests: registro/selección y SourceArtifact+Component válidos, SHA, extensions namespaced, provenance y persistencia neutral. NormalizedFlowResolver acepta entrada sintética sin claves WebForms/VB ni casefold tecnológico. Importación en proceso nuevo prueba independencia del core respecto de implementación concreta. No constituye segundo adapter real/V5.9.

## 12. Fingerprints/cache
Analyzer 2 → 3 por cambio efectivo de implementación; extracción schema 1 y evidencia schema 1.0 intactos. Fingerprint incluye adapters y bundle, junto con analysis neutral; descriptor/version también incluidos. Identidad opcional en build_context aísla adapters/versions mediante config fingerprint. Composición de producción usa referencia cuya identidad está en código fingerprint. Pruebas: modificación de implementación/version cambia guardian; referencia idéntica reutiliza; identidad/version sintética no comparte caché. Documentación/prompts excluidos. Defaults auto/fast/false/None preservados.

## 13. Tests dirigidos
278 tests: 0 fallas, 0 errores, 0 skips; 80.057s. Incluye 12 nuevos de frontera/selección/fake/cache/imports/neutral flow; suites existentes DB (40), caracterización de recorrido (35), normalización, fingerprint, inventario, R2.9/R3. Fixture adicional: 106 archivos, added/removed/changed = 0/0/0.

## 14. Suite completa
`python -X utf8 -m unittest discover -s tests`: 2850 tests, 0 failures, 0 errors, 132 skips históricos; 743.612s (749.965s wall). Primera pasada: 2849 tests, 2 fallas únicamente por cantidad/lista de módulos histórica; 0 errores, 132 skips. Se corrigió el control de 223 → 256 módulos y se fijó inventario AST completo actual, sin regenerar artefactos V4.1. Guardia de fingerprint se actualizó legítimamente a analyzer 3 y rutas canónicas. Pasada final con producción congelada. Incidencias dirigidas resueltas dentro de R1: aliases de patch, mutación de fingerprint verificable, firma anotada de resolve; una ejecución concurrente con edición se descartó y repitió con código congelado.

## 15. Baseline IST usada
Reutilizada full/off V5.3 R3: output/v53r29/f, misma copia output/v53r29/r, config None/max_depth 12/long_paths/AI deshabilitada. Runtime aa7db0d → cierre 9425319 sin cambios; snapshot SHA de referencia revalidado antes del refactor. 15.138 archivos de fuente controlada con hashes iguales a la snapshot R3. La copia hereda 151 comentarios de fixture de calibración V5.3; comparación válida sobre fuente idéntica y declarada, no se presenta como copia prístina. Schemas iguales; analyzer baseline 2 y candidato 3 por invalidación autorizada.

## 16. Corrida IST post-refactor
UNA corrida: `python -X utf8 main.py full output/v53r29/r --output output/v53r29/i --long-paths --cache-mode auto --verify-cache=fast` (CLI invocada por harness instrumentado). Exit 0; AI requested/invoked false; caché final validada y verificada profundamente fuera del tiempo de pipeline. 387.145s wall. Fallback ANALYZER_VERSION_MISMATCH esperado: 0 hits, 8106 misses/files extraídos, 256 shards reconstruidos; ninguna reutilización de extracción antigua. Métricas completas en JSON; no matriz ni changed-ratio/calibración repetida.

## 17. Comparación canónica
Comparador aprobado tools.v5_3_compare_full_incremental, SHA-256: 47524 archivos; 2827997275 bytes en cada árbol; **added=0 / removed=0 / changed=0**. Incluye index, evidence, documentation legacy, documentation_v52, consumer projection, ai_context y todo archivo canónico de baseline. Exclusiones exactas heredadas: RUN_SUMMARY.json, RUN_SUMMARY.md, index/repository.json y directorio _cache_v53. No exclusiones nuevas.

## 18. Performance sanity check
Baseline full/off wall 673.798s; candidato auto wall 387.145s. Output candidato reutilizado permite write-skip y caché analyzer previa invalida; comparación de tiempos orientativa, no benchmark controlado ni atribución de mejora al refactor. Sin multiplicación inexplicada del coste total. Etapas:

| Etapa | V5.3 off s | V5.4 auto s |
| --- | ---: | ---: |
| CALL_RESOLUTION | 0.979 | 1.419 |
| CONTEXT | 38.616 | 31.921 |
| DATABASE_RESOLUTION | 1.255 | 1.813 |
| DEPENDENCY_RESOLUTION | 0.430 | 0.460 |
| DOCUMENTATION | 413.016 | 161.128 |
| EXPORT | 102.522 | 75.893 |
| EXTRACTION | 103.370 | 74.457 |
| FLOW_RESOLUTION | 9.062 | 7.017 |
| SCAN | 0.825 | 0.717 |
| WEB_ENTRY_RESOLUTION | 1.456 | 1.088 |

## 19. Auditoría before/after
62 → 95 módulos en el mismo alcance ampliado por adapter/core nuevos; 223 → 256 módulos de producción total. Imports materiales core evidencia → implementación: 2 → 0; dependencia adicional del recorrido mixto a claves tecnológicas separada. 10 módulos neutrales auditados con 0 imports tecnológicos; MIXED material restante: 0. Clasificación final: `{"CORE": 22, "LEGACY COMPATIBILITY": 30, "LEGACY COMPATIBILITY / DIAGNOSTIC COMPOSITION": 3, "COMPOSITION/ORCHESTRATION": 14, "TECHNOLOGY_ADAPTER": 21, "DB-SPECIFIC CAPABILITY": 5}`. Imports tecnología → core y conteos textuales detallados en JSON. Vocabulario fuera de adapter únicamente en composición/scanner, DTOs/proyecciones legacy, diagnóstico histórico, shims y documentación; esos consumidores no son el Evidence Core neutral. Riesgo heurístico completo: `{"LOW": 138, "MEDIUM": 84, "HIGH": 24, "VERY_HIGH": 10}`. La heurística histórica depende del paquete; trasladar archivos cambia buckets sin demostrar mejora algorítmica.

## 20. Seguridad
Fuente oficial: lectura/inventario/SHA antes y después, 15.138 archivos intactos. Copia controlada: hashes/inventario finales intactos. 0 llamadas reales de provider/IA; guard de tests activo. Exportación usa sanitizador central previo a persistencia; ninguna nueva ruta de evidencia sin sanitización. stdout/stderr runtime capturados en memoria y descartados; artefactos solo métricas/hash/metadatos. Sin source crudo, credenciales ni secretos en reportes.

## 21. Deuda
BLOCKING: ninguna. No bloqueante: shims/DTOs/proyecciones legacy conservados; grandes algoritmos históricos de extracción/normalización/recorrido; complejidad de full_pipeline/pipeline_stages; registro CLI de producción limitado a referencia. Partial resolver recomputation y segunda tecnología real permanecen fuera de alcance. No justifica R2 automáticamente.

## 22. PROJECT_STATE
current_version V5.4; status V5_4_IN_PROGRESS; latest_completed_round V5.4-R1; latest_approved_round V5.3-R4; round_status V5_4_R1_READY_FOR_HUMAN_REVIEW; human_review PENDING; next HUMAN_REVIEW; v5_4_closed false. Contadores históricos globales de IA preservados; contadores propios R1 = 0.

## 23. Continuidad
Ambos documentos actualizados solo mediante encabezado vigente y ledger agregado. Historia anterior conservada. Modelo V5.4+: R1 Integrated Delivery → R2 Targeted Corrections only if needed → R3 Final Verification & Closure, target máximo 3 rondas.

## 24. Git
main; HEAD=origin/main `9425319cb2edbae896b96f7abfbdcd3764beb538`; ahead/behind 0/0. Backup `2cb317fe5ae3dd2cbad1f865b1faee4a50a99569` intacto. Sin commit/push/tag/amend/rebase/reset/clean/staging. Administrativos V5.3 pendientes: docs/V5/V5_3_R4_1_GIT_PUSH_RESULT.md y prompts/V5/V5_3_R4_1_FINAL_GIT_PUSH.md preservados, SHA registrados. Prompt activo preservado. Estado exacto en JSON; checkpoint solo tras revisión/aprobación explícita.

## 25. Recomendación
**V5_4_NEXT_R3_FINAL_VERIFICATION**. Directo R3 si revisión humana aprueba; no ejecutar ahora. R2 solo ante defectos reales encontrados por revisión.

## 26. Estado final
**V5_4_R1_READY_FOR_HUMAN_REVIEW**. R1 integrada completa técnicamente; V5.4 abierta, revisión pendiente; V5.5 y rondas siguientes no iniciadas.
