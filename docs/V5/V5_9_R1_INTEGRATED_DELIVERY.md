# V5.9 R1 — Integrated Delivery: Real Multi-Technology Pilot

Fecha: 2026-10-08. Estado: **`V5_9_R1_READY_FOR_HUMAN_REVIEW`**. Recomendación: **`V5_9_NEXT_R3_FINAL_VERIFICATION`**.
Evidencia: [JSON](V5_9_R1_INTEGRATED_DELIVERY.json) · [matriz](V5_9_R1_MULTI_TECH_PILOT_MATRIX.json) · [inventario de segunda tecnología](V5_9_R1_SECOND_TECH_INVENTORY.json) · [mantenibilidad](V5_9_R1_MAINTAINABILITY_INVENTORY.json).

```text
pilot_kind = SELF_HOSTED_CIRCULAR
second_source_is_legacy_mapper_itself = true
external_independence_claim = false
real_second_technology = true
independent_external_product = false
```

**Interpretación permitida:** V5.9 demuestra que la arquitectura V5 procesa al menos dos stacks distintos (VB.NET WebForms/Oracle y Python) con contratos comunes. **No permitida:** que pruebe generalización independiente a sistemas externos arbitrarios; eso requiere un corpus externo futuro.

## 1. Objetivo

Piloto multi-tecnología con el mismo core V5: segundo adapter real, Evidence neutral, templates, cache incremental, Fake provider, segmentación, review/canonical, consumers/plugins y regresión IST.

## 2. Estado y trayectoria de la ronda

V5.8 CLOSED y publicada (`bcb8d57097ec769da75f5fc7207b9a6db295e374`); `main` = origin/main, 0/0. **Gate A inicial: `V5_9_R1_BLOCKED_SECOND_TECH_SOURCE`** (sin aplicación real/local de otra tecnología). **El humano autorizó expresamente el piloto circular Python** y R1 se **reanudó en la misma ronda** (sin R1.1/R1B/R2), actualizando estos mismos entregables. La anterior decisión de bloqueo queda en el historial del inventario JSON.

## 3. Fuentes

`AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.json`, ambos prompts de V5.9, ambos roadmaps; código: `adapters/` (contratos y adapter de referencia), `evidence/`, `cache/`, `fingerprints/`, `documentation_v52/`, `context/`, `consumers/`, `review/`, `cli/pipeline_stages.py`, `full_pipeline.py`, `main.py`.

## 4. Descubrimiento de corpus

Ver el inventario JSON: 8 candidatos inspeccionados (IST y copias, LegacyMapper, `site-packages`, scripts utilitarios, SQL Developer, binarios) y rechazados; tras la autorización humana, el corpus es la copia congelada autorizada.

## 5. Selección y fuente congelada

`SECOND_TECH_SOURCE_ID = SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60`. Origen autorizado `C:\PruebasLegacyMapper\LegacyMapper` (commit `e9e3d60`, V4.2-R8: **anterior a todo adapter V5**, sin contaminación por el adapter nuevo). Copia congelada = `git archive e9e3d60` (solo archivos versionados; 3 `.py` sin versionar del origen excluidos) en `output/_local_v59r1/python_source`; el origen nunca se modificó ni se ejecutó. Se excluyó la carpeta `fixtures` (fixtures VB de sus tests; volverían mixto el repositorio). `dist` no forma parte del árbol versionado.

## 6. Baseline

- **Python:** 540 archivos escaneados (243 `.py`, 5 795 557 bytes totales, 2 023 806 de Python), tree hash `a190898bd89683a8ae443fd9d0640e37fc454327ceea34cacdd818c2862ce39e`; sin `pyproject/setup/requirements`; 4 proyectos (directorios de primer nivel: `(root)`, `legacy_documenter` 169 archivos, `tests` 62, `tools` 11); 243 módulos, 644 clases, 2 721 funciones/métodos; 1 985 imports; 16 145 call sites; 73 candidatos de entry point (guards `__main__`); 692 candidatos de operación de archivo; red/provider: `asyncio`, `copilot`, `urllib`; datos: solo sistema de archivos (sin drivers DB). Parsing estático puro: LegacyMapper no se ejecutó como target.
- **IST (revalidado):** 15 138 archivos, SHA-256 `77965c64…fcd792e5`, salida de referencia 47 523 archivos / 2 828 066 791 bytes; `ANALYZER_VERSION=3`.

## 7. Adapter `python-generic` 1.0

Paquete `legacy_documenter/adapters/python_generic/` (8 módulos, 1 077 líneas; el adapter de referencia tiene 2 668): `source_parser` (ast, sin ejecutar), `extraction` (cache-aware, proyectos), `resolution` (llamadas/entries), `analysis` (operaciones de archivo, dependencias, flujos sobre el recorrido neutral), `normalization` (Evidence), `adapter`, `_names` (tablas de nombres congeladas, para que el resultado no dependa del intérprete). Contrato V5.4 reutilizado (sin contract v2). Alcance: módulos/clases/funciones, entry points `if __name__ == "__main__"`, imports → paquetes externos, llamadas resolubles conservadoras, límite de sistema de archivos, flujos/paths. Resolución determinista y conservadora: función/clase local o importada, `self.m()` con bases conocidas, `Cls.m()`, `mod.f()`, re-export vía `__init__`, `Cls(...).m()` y locales de asignación única `x = Cls(...)`; builtins/stdlib/terceros = *externo* confirmado; todo lo demás **unresolved**. Nada se inventa para subir cobertura.

## 8. Evidence neutral

Sin entidades nuevas en el core (guard: las clases de `evidence/entities.py` son las mismas nueve). Mapeo: módulo/clase → `Component`, import de tercero → `ExternalDependency(package)`, llamadas → `CallIdentity`, clases instanciadas → `Instantiation`, fronteras → `UnresolvedBoundary`, operaciones de archivo → `data_access` (passthrough). Conteos (Python / IST): SourceArtifact 540 / 15 138; Project 4 / 259; Component 887 / 9 859; EntryPoint 73 / 12 662; Call 16 145 / 230 356; ExternalDependency 1 / 4 839; DataOperation 692 / 20 082; DataObject (SP/SQL) 0 / 5 392 (no se inventa); FunctionalFlow 19 / 12 642; FunctionalPath 4 600 / 170 020; UnresolvedBoundary 4 191 / 162 914; EvidenceReference (refs de provenance) 22 514 / 454 010. Estados Python: calls 9 377 confirmed / 6 768 unresolved; data_access 289 confirmed / 403 inferred; entry points 19 confirmed / 54 unresolved (`unittest.main`, externos); paths 282 / 145 / 4 173. Schema `1.0` en ambos; `validate_evidence` (I-1, sha256, I-4/I-5) pasa en cada corrida.

## 9. Provenance

Cada entidad conserva `SourceArtifact` + línea (cuando existe), `adapter_id`/`adapter_version` (en `adapter` del artifact/proyecto y `extensions`) e identidad determinista (`sha256_id`/`poly33_id`); cuentas por adapter verificadas en `source_artifacts` (`python-generic` / `vbnet-webforms-oracle`).

## 10. Unresolved

Preservado en tres niveles: llamadas con receptor de tipo desconocido (`obj.m()`, `self.attr.m()`), callee de entry externo y fronteras de flujo. Nunca se promueve a confirmed sin evidencia determinista (las operaciones de archivo por nombre de método de `pathlib` quedan `inferred`).

## 11. Templates (V5.2) — hallazgo y corrección

**Hallazgo:** el catálogo es-ES y `transform.py` contenían vocabulario .NET (solución `.sln`, `.vbproj`, «pantallas», procedimientos almacenados) y `transform` etiquetaba como `vb_source` todo símbolo y contaba `source_files` solo sobre `vb_source` (Python daba «0 archivos de código fuente», «73 pantallas»). **Corrección, sin fork de template/renderer:** (a) `overlay` de terminología **solo de datos** (`defaults/i18n/terminology/python-generic.es.json`, 43 claves validadas contra el catálogo) seleccionado por el adapter vía un id opaco (`documentation_terminology`); (b) etiqueta de archivo por extensión (`.py` → `python_source`); (c) `source_files` suma los kinds de código. El catálogo por defecto solo ganó 2 claves aditivas, así que los documentos IST son byte-idénticos (0/0/0). Resultado Python: «243 archivos de código fuente Python», «73 módulos con punto de entrada»; las menciones residuales de WebForm/Oracle/vbproj en los documentos son **datos del corpus** (nombres de símbolos de LegacyMapper como `VBProjExtractor`), no de la capa neutral. Perfiles `human-functional` y `human-technical` generados para ambos stacks (Python: 4 640 archivos en el árbol de salida).

## 12. AI context

`ai_context/` y paquetes `AI_HYDRATED_PROJECTION` con los contratos V5.5 sin cambios; `READ_AI_CONTEXT` OK sobre Python, 0 llamadas a provider.

## 13. Cache cold / warm / incremental (V5.3)

Neutralización mínima: `python_source` en `ANALYZED_FILE_TYPES` (hash semántico/extraction cache) y en `CODE_TYPES` del scope (el guard «tipos analizados = mapa de extractores» ahora es la unión de adapters). Mediciones (Python, `--long-paths`, AI OFF):
- **Cold:** 56.8 s; 243 misses; DOCUMENTATION 48.5 s, EXTRACTION 1.7 s, FLOW 0.25 s, EXPORT (evidence incl.) 3.0 s.
- **Warm sin cambios:** 7.1 s; **243 hits / 0 misses**; árbol de salida (4 640 archivos) byte-idéntico al cold.
- **Determinismo:** segunda corrida cold en directorio nuevo → 4 640 archivos, 0/0/0 vs la primera.
- **Un archivo cambiado (copia controlada, `utils/sanitizer.py` +1 función +1 llamada interna):** 7.0 s; **242 hits / 1 miss / 1 archivo re-extraído**; salida: 17 archivos cambiados + 1 añadido de 4 641; **idéntica a una corrida cold de la copia mutada**. El scope reporta `mode=full` + `SOURCE_IN_PROJECT` (todo cambio de código es de resolución global: criterio conservador heredado); el recómputo acotado es el de extracción, igual que en IST. Fuente original intacta.

## 14. Coexistencia y wrong-adapter (V5.4)

`AdapterRegistry([ReferenceAdapter, PythonGenericAdapter])`; selección por kinds observados; repo mixto → `AdapterSelectionError`; sin adapter → `UNSUPPORTED_TECHNOLOGY`. Cada adapter extrae vacío ante la otra tecnología (IST+python → not-applicable; Python+vbnet → not-applicable; tests con fixtures). Las etapas posteriores se enrutan al adapter que extrajo (`adapter_of`); `build_evidence_artifacts` y la terminología seleccionan por los kinds del run.

## 15. Fake provider (V5.5)

Corpus real + `FakeAIProvider` que cita una referencia tomada del propio contexto: `SUCCESS`, 1 request, propuesta `READY_FOR_REVIEW`, envelope `PENDING_TECHNICAL_LEAD_REVIEW`, `canonical=false`, aprobación del Technical Lead falsa, 0 intentos de resolver provider real. El adapter no importa providers (guard AST).

## 16. Segmentación (V5.6)

**REAL:** flujos reales de Python exceden el presupuesto por defecto (16 000 caracteres): `FLOW-0042743202` (147 grupos de path, 197 104 caracteres) → **108 segmentos** `partial=true`, unión de `included_paths` = paths del padre, sin solape, cada uno con `omitted_paths` y refs; otros flujos fallan cerrado `BUDGET_IMPOSSIBLE_AFTER_SEGMENTATION` salvo con mayor presupuesto (como en IST). **`NOT_TRIGGERED_REAL`:** segmentación dentro de la *request* de IA (V5.6 `segmented_context`): el selector eligió flujos que caben; con ventanas menores el run falla cerrado (`CONTEXT_TOO_LARGE`, 0 propuestas), nunca trunca en silencio. **CONTROLLED_FIXTURE:** flujo Python grande sintético segmentado por el contrato neutral (test).

## 17. Review / canonical (V5.7)

Sobre **copia** del artifact Fake: `prepare` → APPROVE simulado → canonical (`CAN-…`) con readback igual y cadena de auditoría completa (decision, snapshot, baseline, canonical, fingerprint); artifact original sin `knowledge/`. No se aprobó nada real.

## 18. Stale guard

Sobre otra copia: `prepare` → se altera la evidencia referenciada → APPROVE → **`PROPOSAL_STALE`**, sin canonical.

## 19. Consumers / plugins (V5.8)

Contrato 1.0 sin cambios sobre la salida Python: `READ_EVIDENCE`, `READ_FLOW`, `READ_PARTIAL_FLOW` (108 segmentos reales), `READ_AI_CONTEXT`, `RENDER_HUMAN_DOC` (funcional y técnico), `EXPORT_JSON` OK; `READ_CANONICAL` y `READ_REVIEW_HISTORY` (audit chain verificada) sobre la copia controlada; dos lecturas idénticas en bytes. Mismo manifest Fake V5.8: `READ_FLOW`/`READ_EVIDENCE` OK, capability no declarada → `UNSUPPORTED_CAPABILITY`, escritura → `READ_ONLY_VIOLATION`. Sin Plugin Runtime.

## 20. Matriz del piloto

Ver [matriz JSON](V5_9_R1_MULTI_TECH_PILOT_MATRIX.json) (17 filas, estados `REAL`/`CONTROLLED_FIXTURE`; ninguna `FAIL`): REAL = detección de adapter, Evidence, provenance, unresolved, docs ×2, AI context, cache cold/warm/incremental, Fake provider (corpus real, provider Fake), segmentación (flujo real), ConsumerFacade, runtime independence; CONTROLLED_FIXTURE = review baseline, canonical y plugin (copias/manifest Fake). Las celdas IST no re-ejecutadas en V5.9 citan la ronda de su evidencia real.

## 21. Cobertura (Python / IST)

Archivos fuente 243 / 4 328 `vb_source` (+177 aspx, 3 165 ascx); proyectos 4 / 259; componentes 887 / 9 859; entry points 73 / 12 662; llamadas 16 145 / 230 356; operaciones de datos 692 (archivos) / 20 082 (DB); dependencias externas 1 / 4 839; paths 4 600 / 170 020; flujos 19 / 12 642; unresolved 6 768 llamadas, 4 191 fronteras / 217 581, 162 914. Las proporciones no son comparables entre stacks (naturaleza distinta del código).

## 22. Muestra de revisión humana

**45 elementos** (8 entry points, 9 llamadas internas incl. 4 por receptor de instanciación, 5 externas, 6 unresolved, 1 dependencia externa, 10 operaciones de archivo, 6 fronteras): **45 correctos, 0 incorrectos, 0 inciertos**, contrastando cada elemento con su línea de código. Limitaciones: revisor = el asistente implementador (no un humano independiente), muestreo por paso sobre registros ordenados, tamaño pequeño; **no se extrapola precisión global**. Riesgos conocidos no cubiertos por la muestra: locales que ocultan un import, `self.attr.m()` (queda unresolved), despacho dinámico/decoradores, handlers de `argparse`.

## 23. Determinismo

Dos corridas cold equivalentes → salidas idénticas (4 640 archivos, 0/0/0); warm idéntico al cold; incremental idéntico al cold de la copia mutada; `READ_FLOW` repetido idéntico en bytes; la extracción serializada es igual entre corridas (test).

## 24. Colisiones

Entre IST y Python no coincide ningún id de EP, EVB, FLOW, PATH, DAO, Component, CallIdentity, Project, ExternalDependency ni UnresolvedBoundary. La única coincidencia es un `SourceArtifact` (`SRC-b1fb90c6…`) de la ruta relativa `.gitignore` presente en ambos repos: la identidad `SRC-` es por ruta relativa **dentro de un repositorio** (contrato V5.1, no cambiado), por lo que es esperable y no cruza entidades. Nombres similares: Python tiene `main` ×2, `service` ×9, `config` ×1 símbolos; IST 0 con esos nombres cortos; ids distintos por construcción. Contrato de IDs sin cambios.

## 25. Runtime independence

Guards AST/import: el adapter Python lo importa solo `cli/pipeline_stages.py` (composition root); core/evidence/context/cache/consumers/plugins/review/llm/docs no lo importan ni nombran `python-generic`; el adapter no importa CLI, provider, consumers, review, knowledge ni context; las capas neutrales no importan ningún adapter salvo los dos shims V5.4 preexistentes (`evidence/builder.py`, `evidence/projection.py`). Menciones neutrales a la etiqueta de kind `python_source`: solo `scanner/file_classifier`, `cache/scope`, `fingerprints/semantic` y `documentation_v52/transform` (etiquetas de kind, igual que `vb_source`).

## 26. Seguridad

Sin red; el target es dato: solo `ast.parse` (sin `import`, `exec`, `eval`, `compile`, `subprocess`, `importlib`, red; guard AST sobre el paquete + test con un target que escribiría un archivo y haría `os.system`: no se ejecuta ni se importa); no se instalaron dependencias; la fuente original y la copia congelada no se modificaron (mutación solo en copia descartable); errores de parseo registran clase y línea, nunca texto de fuente; sin secretos en artifacts (sanitizer central).

## 27. Regresión IST completa

Una corrida oficial post-cambio, AI OFF, `--long-paths`, cache auto, salida nueva: **SUCCESS, 656.6 s (cold, `NO_CACHE`), 8 106 archivos extraídos, pico de memoria ≈3.0 GB**; comparación contra la salida de referencia V5.8-equivalente: **47 523 archivos, 2 828 066 791 bytes, added=0, removed=0, changed=0**, exclusiones sin ampliar (RUN_SUMMARY, `_cache_v53`, `index/repository.json`). Fuente IST antes/después: 15 138 archivos, SHA-256 `77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5`, sin cambios. Provider real: 0 intentos.

## 28. Performance

Python (cold, 243 archivos; rango de 4 corridas cold 51–58 s): detección de adapter 3.3 µs (selección sobre 540 kinds); extracción 1.1–1.7 s (≈5 ms/archivo); resolución de llamadas 0.04–0.11 s; flujos 0.2–0.35 s; Evidence+export 2.5–3.0 s; documentación 44–52 s (4 640 archivos); warm 7 s; incremental 7 s. IST (cold): extracción 69 s, flujos 6.6 s, export/evidence 82 s, documentación 446 s, total 656.6 s (rondas previas 797–875 s con otra carga de máquina; sin regresión material). Consumers: carga de índices y lecturas en milisegundos.

## 29. Tests

Nuevo `tests/test_v5_9_r1_python_adapter.py`: **30 tests** (aplicabilidad/wrong-adapter, parsing, resolución, entries, operaciones de archivo, flujos, Evidence válida/neutral/determinista, cache de extracción y de capa, seguridad/no ejecución, leakage e independencia, contratos cross-tech con VB y Python bajo las mismas aserciones, colisiones, consumers sobre ambos, segmentación controlada). Pins actualizados con razón: fingerprint (2 tests), guards «tipos analizados = unión de adapters» (2), clasificación del parámetro `terminology`, inventario de mantenibilidad (282 → 290 módulos + snapshot V5.9), guard de importaciones dinámicas (ignora la tabla de nombres `_names.py`). Dirigidos V5.1–V5.8 + nuevos: **867 tests**. Suite completa: **3083 tests, 0 failures, 0 errors, 132 skips** (baseline 3053 + 30).

## 30. Mantenibilidad

Módulos de producción 282 → 290; adapter Python 1 077 líneas en 8 módulos con responsabilidades separadas (parser / extracción / resolución / análisis / normalización / adapter / tablas), sin monolito; menciones de strings tecnológicos fuera de `adapters/`: etiqueta `python_source` en 4 módulos neutrales; imports de providers en el adapter: 0; archivos neutrales tocados (11) con cambios mínimos y aditivos. Detalle en el inventario de mantenibilidad.

## 31. Fingerprint y cache

`ANALYZER_CODE_FINGERPRINT`: **`4f7600f0…eb1ec6` → `ce21000dfe5c64c4ad8af70c1dcb240eeb9d342bdf06d72220b7be7cbd39d2d7`**. Razón legítima: el directorio `adapters/` y el scanner participan del fingerprint, se añadió código analizador (adapter nuevo, kind `.py`, enrutamiento de etapas). Invalidación esperada: las extraction caches existentes se invalidan una vez (el fingerprint forma parte de cada clave); la corrida IST fue cold por eso. `ANALYZER_VERSION=3` **sin cambio**: no hay incompatibilidad de formato y la salida VB quedó probada idéntica en la corrida real.

## 32. Deuda

- **BLOCKING:** ninguna.
- **OBSERVATION:** `SELF_HOSTED_CIRCULAR_PILOT` (el corpus es LegacyMapper mismo); resolución sin inferencia de tipos (≈42 % de las llamadas Python quedan unresolved); entry points solo por `__main__` (sin `argparse`/console_scripts); el scope incremental marca `mode=full` para todo cambio de código; residuo de vocabulario .NET en claves de campo internas (`webform`) y en el catálogo por defecto para IST (intencionalmente intacto); lista stdlib congelada con CPython 3.14.
- **FUTURE_PHASE:** validación independiente de una segunda tecnología con corpus externo; inferencia de tipos más rica; adaptadores de DB adicionales; Plugin Runtime; tercera tecnología.

## 33. PROJECT_STATE

`V5.9`, `V5_9_IN_PROGRESS`, completed `V5.9-R1`, approved `V5.8-R3`, `round_status = V5_9_R1_READY_FOR_HUMAN_REVIEW`, human PENDING, `v5_9_closed=false`, next HUMAN_REVIEW, `second_technology=Python`, `second_adapter_id=python-generic`, `second_source_id`/hash, `pilot_kind=SELF_HOSTED_CIRCULAR`, `external_independence_claim=false`; el bloqueo de fuente se retiró como estado activo y se conserva en `v5_9_r1_history`.

## 34. Continuidad

Ambos roadmaps: V5.8 CLOSED, V5.9 R1 con el bloqueo inicial, la autorización y la reanudación, adapter, matriz, R2 solo por defecto real (no se detectó ninguno), V5 Closure no iniciada.

## 35. Git

Solo consultas. `main`, HEAD = origin/main = `bcb8d57097ec769da75f5fc7207b9a6db295e374`, 0/0. Recibo post-push V5.8 presente (único cambio administrativo previo, preservado). Cambios locales: producción (scanner, `adapters/contracts.py`, `cli/{pipeline_stages,full_pipeline}.py`, `main.py`, cache/fingerprints/documentation_v52 mínimos), `adapters/python_generic/` nuevo, tests, docs, `PROJECT_STATE.json`, roadmaps, prompts V5.9. Sin commit, push, tag, amend, rebase, reset ni clean.

## 36. Recomendación R2/R3

Sin defecto real que justifique R2: sin leakage, contrato normalizado válido, cache correcto cross-tech, sin regresión IST, sin colisiones, parcial preservado, stale guard efectivo, consumers/plugins compatibles, suite verde. (El hallazgo de vocabulario V5.2 y las incompatibilidades de cache se detectaron y resolvieron dentro de R1.) **`V5_9_NEXT_R3_FINAL_VERIFICATION`.** Estado final: `V5_9_R1_READY_FOR_HUMAN_REVIEW`; detenido para revisión humana; V5 Closure no iniciada.
