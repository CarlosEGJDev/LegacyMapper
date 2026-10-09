# V5.9 R2 — Targeted Corrections: Cross-Repository SourceArtifact Identity

Fecha: 2026-10-08. Estado: **`V5_9_R2_READY_FOR_HUMAN_REVIEW`**. Recomendación: **`V5_9_NEXT_R3_FINAL_VERIFICATION`**.
Evidencia: [JSON](V5_9_R2_TARGETED_CORRECTIONS.json) · [impacto de identidad + inventario](V5_9_R2_IDENTITY_IMPACT.json).
Piloto sin cambios de naturaleza: `second_technology=Python`, `second_adapter_id=python-generic`, `pilot_kind=SELF_HOSTED_CIRCULAR`, `external_independence_claim=false`.

## 1. Defecto

Dos repositorios con la misma ruta relativa producían el mismo `SRC-`. Evidencia R1: IST 15 138 artifacts, Python 540, **1 id compartido** (`SRC-b1fb90c6…`, ruta `.gitignore`). El resto de familias cross-tech: 0 colisiones. R2 corrige exactamente esto; no se tocó el alcance del adapter Python, ni el Consumer Contract, ni otras familias de ID.

## 2. Medición pre-fix

- **Fórmula:** `SRC-` + SHA-256 del JSON canónico `["SRC", ruta relativa POSIX]`; sin ninguna entrada de repositorio (contrato V5.1 R1 y docstring de `SourceArtifact`).
- **Dónde se calcula:** `adapters/vbnet_webforms_oracle/normalization.py` (5 llamadas + 3 helpers de módulo) y `adapters/python_generic/normalization.py` (1 helper).
- **Qué contiene `SRC-`:** solo `evidence/` (5 archivos de partición en la corrida Python); `index/`, `ai_context/`, `documentation_v52/` y `consumer_projection/` no.
- **Tests con pins:** ninguno fija un hash literal de `SRC-` (`test_v5_1_r2_normalized_evidence_core`, `test_v5_2_r3_3_component_navigation` lo derivan).
- **Identidad de repositorio existente:** `cache/identity.py` = **ruta absoluta normalizada** (solo localidad de cache; prohibida como identidad por el prompt). No existía un identificador lógico estable.

## 3. Contrato actual

V5.1 fija `SRC-` = f(ruta) y no define identidad de repositorio ni su evolución. R2 no rompe el contrato cerrado: añade una evolución **opt-in**.

## 4. Diseño

```text
repository_id declarado  →  SRC = sha256_id("SRC", repository_id, ruta_relativa_posix)
repository_id no declarado →  SRC = sha256_id("SRC", ruta_relativa_posix)   (fórmula V5.1 sin cambios)
```

Una única función neutral `evidence/identity.source_artifact_id(path, repository_id)` es ahora el único lugar donde se mintea un `SRC-` (ambos adapters la usan). La forma con id tiene distinta aridad que la legacy, de modo que un espacio declarado nunca coincide con el no declarado. Entradas prohibidas respetadas: sin ruta absoluta, máquina, usuario, timestamp ni UUID (test sobre el código de la función).

## 5. Repository identity

Se diseñó la mínima necesaria porque no existía una usable: un **nombre lógico declarado** por una persona (`--repository-id` en `analyze`/`full`, `repository_id=` en las APIs), validado como nombre (1–128 chars `[A-Za-z0-9][A-Za-z0-9._:-]`, rechaza rutas, separadores, espacios y vacío). Va en `indexes["repository"]["repository_id"]` y en `EVIDENCE_MANIFEST.json` **solo cuando se declara**. No es una segunda noción incompatible: la identidad física de la cache (ruta raíz) sigue siendo local y distinta por diseño, y el id lógico no la reemplaza ni depende de ella. Clasificada en `CLI_OPTION_CLASSES` como `repository-identity`.

## 6. Compatibilidad

- **Sin id declarado: `IDENTITY_COMPATIBLE`** — todos los ids y baselines existentes (IST incluido) quedan idénticos.
- **Con id declarado:** evolución aditiva opt-in; no se migró ni rebaselinó nada. **Limitación honesta:** dos repositorios que se analicen *sin* declarar identidad siguen compartiendo el espacio V5.1 (por eso la colisión se evita declarando; el piloto Python ahora declara `SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60` e IST permanece sin declarar). Hacer obligatoria la declaración cambiaría los ids de IST (escenario B), decisión que se deja a la revisión humana.

## 7. Impacto en IDs derivados

Ver la tabla completa en el JSON. `CHANGED_BECAUSE_DEPENDS_ON_SRC` (solo con id declarado): `SourceArtifact`, `EvidenceReference` de origen y las claves foráneas a `SRC-` (`Component.source_ref`, `CallIdentity.source_artifact`, `Instantiation.source_artifact`, provenance de Project/Solution/DataObject/ExternalDependency). `UNCHANGED`: `PRJ-`, `SOL-`, `CMP-`, `CAL-`, `XDP-` (siguen siendo función de rutas; misma propiedad latente, no observada colisionando → observación). `UNAFFECTED_BY_DESIGN`: `EP-`, `EVB-`, `FLOW-`, `PATH-`, `UNB-`, `DAO-`, claves de cache, AI context/hidratación, `CRES-`, baseline/snapshot/canonical (refs DAO/PATH, fingerprints sobre registros de índice). Test: con y sin id, esas familias son idénticas y `SRC-` es disjunto.

## 8. Implementación

`evidence/identity.py` (`normalize_repository_id`, `source_artifact_id`); ambos `normalization.py` usan la función (helpers VB con parámetro opcional); `evidence/persistence.py` escribe `repository_id` en el manifest solo si existe; `cli/parser.py` (`--repository-id`, validación argparse), `cli/router.py` (reenvía solo si se declara, por lo que las llamadas sin id no cambian), `cli/full_pipeline.py`, `main.py`, `fingerprints/configuration.py` (clasificación). Sin imports del adapter Python en core/evidence/cache/consumers/review/docs/provider (test). Un defecto propio detectado y corregido durante R2: una llamada a `_whole_file_source_ref` en el dict de proyectos VB quedó sin namespace y el invariante I-5 falló cerrado en la primera corrida con id declarado; el test cross-tech lo detectó y se corrigió.

## 9. Tests de colisión

`tests/test_v5_9_r2_source_identity.py` (17 tests): misma ruta + distinto id → distinto `SRC` (y sin ningún `SRC` compartido en todo el árbol); mismo id + otro root absoluto → ids y particiones idénticos; id no declarado = fórmula V5.1; el id rechaza rutas/espacios/vacío; repo declarado no filtra nombres de directorio físicos en la identidad.

## 10. Relocation

Corpus Python congelado analizado desde dos roots físicos distintos (otro padre y otro nombre de directorio): **mismos 540 `SRC-` y todas las particiones de evidence idénticas salvo las que contienen el root físico por diseño** (`scan_summary.json` y su hash en `EVIDENCE_MANIFEST.json`). Árbol completo: 7 archivos distintos de 4 640, todos imprimen el root/nombre de directorio (`scan_summary`, manifest de evidence, `SYSTEM_CONTEXT.json`, dos documentos del árbol `documentation/`, `general/README.md` —el nombre del sistema sale del directorio—, y el `MANIFEST.json` de docs que hashea esos); ninguno es identidad. Observación preexistente, no tocada.

## 11. Inventario cross-tech (IST vs Python)

Con el id declarado en Python: **SourceArtifact compartidos = 0** (antes 1), y 0 en Project, Component, EntryPoint, EventBinding, Call, FunctionalFlow, FunctionalPath, DAO, ExternalDependency y UnresolvedBoundary. Reproducción del defecto en la misma medición: el mismo corpus Python **sin** declarar sigue compartiendo `.gitignore` con IST.

## 12. Cache

Antes: el extraction cache y el File State se clavan por ruta + hash + fingerprint; los registros de extracción no llevan `SRC-`; el evidence se reconstruye en cada corrida. Ahora: igual. Prueba: misma carpeta de salida, cambiar de id → sesión `warm`, **243 hits / 0 misses**, y los `SRC-` nuevos son disjuntos de los anteriores (sin ids obsoletos), manifest con el id nuevo. Invalidación esperada: ninguna adicional por la identidad; el fingerprint del analyzer sí cambió (§18) e invalida una vez las caches existentes. Corridas Python: cold 52.0 s, warm 6.8 s (243 hits), segunda cold idéntica byte a byte (0/0/0 sobre 4 640 archivos), warm idéntico.

## 13. Evidence invariants

Con id declarado, para VB y Python: `validate_evidence` (I-1, sha256, I-4/I-5: refs y provenance resuelven, sin referencias colgantes), schema 1.0, determinismo de ids (dos builds), unresolved preservado (corrida Python 4 191 fronteras, igual que R1).

## 14. Review / canonical

Sobre copia controlada de un artifact Fake con id declarado: refs de la propuesta resuelven, `prepare` fija baseline, APPROVE simulado → canonical con readback igual y cadena de auditoría válida; alterar la evidencia referenciada → `PROPOSAL_STALE` (sin falso negativo ni referencias huérfanas silenciosas); artifact original sin `knowledge/`. Estos objetos no contienen `SRC-`.

## 15. ConsumerFacade

Contrato 1.0 sin cambios: `READ_EVIDENCE`, `READ_FLOW`, `READ_PARTIAL_FLOW` (flujo real, 108 segmentos, unión = padre, sin solape), `READ_AI_CONTEXT`, `RENDER_HUMAN_DOC` ×2, `EXPORT_JSON` OK; `READ_CANONICAL` y `READ_REVIEW_HISTORY` (audit chain verificada) OK sobre la copia controlada; lectura repetida idéntica en bytes.

## 16. Python rerun

`SECOND_TECH_SOURCE_ID=SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60`; tree hash antes y después `a190898b…ce39e` (**fuente intacta**); 0 llamadas a provider real (guard); sin ampliar el adapter.

## 17. Regresión IST

Una corrida real post-cambio (AI OFF, sin id declarado → escenario A): **SUCCESS, 651.7 s (cold), pico ≈3.0 GB; 47 523 archivos, 2 828 066 791 bytes, added=0, removed=0, changed=0** contra la referencia V5.8-equivalente, exclusiones sin ampliar; fuente IST 15 138 archivos, SHA-256 `77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5`, sin cambios.

## 18. Fingerprint y versión

`ANALYZER_CODE_FINGERPRINT`: `ce21000d…` (R1) → **`f05b2de43b726e75e03b97e1d35fef8b3407d54247e0a4e4537ab24d282fa26b`** (código de ambos adapters cambió). `ANALYZER_VERSION=3` sin cambio: sin incompatibilidad de formato; la salida VB/IST quedó probada idéntica. Pins actualizados con razón: fingerprint (2 tests), inventario de mantenibilidad (snapshot nuevo; 290 módulos sin cambio).

## 19. Tests dirigidos

V5.1 identidad/evidence, V5.3 cache/fingerprints/scope, V5.4 adapters, V5.2 docs, V5.5 AI, V5.6 segmentación, V5.7 review/canonical, V5.8 consumers, V5.9 R1+R2, guards de arquitectura, provider guard, mantenibilidad: **627 tests, OK** (156 s).

## 20. Suite completa

`python -X utf8 -m unittest discover -s tests`: **3100 tests, 0 failures, 0 errors, 132 skips** (623.5 s; baseline R1 3083 + 17).

## 21. Runtime independence

El fix es neutral: `evidence/` no menciona `python-generic`; cache/consumers/review/llm/context/docs no importan ningún adapter; el adapter Python sigue importado solo por el composition root.

## 22. Security

La identidad no incluye ruta absoluta, usuario, máquina, timestamp, UUID ni secretos (test sobre la fuente de `source_artifact_id` y sobre la salida); el id declarado se valida como nombre y se sanitiza en la CLI.

## 23. Deuda

- **RESUELTA:** `CROSS_REPOSITORY_SOURCE_ARTIFACT_ID_COLLISION` (para repositorios con identidad declarada; el piloto la declara).
- **BLOCKING:** ninguna.
- **OBSERVATION:** `SELF_HOSTED_CIRCULAR_PILOT`; repositorios sin identidad declarada comparten el espacio V5.1 (decisión de volver obligatoria la declaración = escenario B, para revisión humana); `PRJ-`/`CMP-`/`CAL-`/`XDP-` siguen siendo función de rutas (no observado colisionando); salidas que imprimen el nombre del directorio raíz.
- **FUTURE_PHASE:** validación independiente de una segunda tecnología con corpus externo.

## 24. PROJECT_STATE

`V5.9`, `V5_9_IN_PROGRESS`, completed `V5.9-R2`, approved `V5.8-R3`, `round_status=V5_9_R2_READY_FOR_HUMAN_REVIEW`, human PENDING, `v5_9_closed=false`, next HUMAN_REVIEW; piloto Python/`python-generic`/`SELF_HOSTED_CIRCULAR`/`external_independence_claim=false` conservados.

## 25. Git

Solo consultas. `main`, HEAD = origin/main = `bcb8d57097ec769da75f5fc7207b9a6db295e374`; los cambios V5.9-R1 y R2 siguen locales; recibo post-push V5.8 presente. Sin commit, push, tag, amend, rebase, reset ni clean; sin R2.1/R2.2.

## 26. Recomendación

Sin defecto abierto: colisión resuelta con proof, IST byte-idéntico, suite verde. **`V5_9_NEXT_R3_FINAL_VERIFICATION`** (R3 de V5.9 incluirá el commit/push de R1+R2 solo si su prompt lo autoriza).

## 27. Estado final

`V5_9_R2_READY_FOR_HUMAN_REVIEW`. Detenido para revisión humana; V5 Closure no iniciada.
