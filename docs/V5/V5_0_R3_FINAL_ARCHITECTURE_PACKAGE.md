# V5.0 R3 — Final Architecture Package

## STATUS

`V5_0_R3_READY_FOR_PRE_V5_1_GATE`

Ronda estrictamente documental. No se modificó producción, tests, CLI, providers ni `PROJECT_STATE.json`. No se ejecutó IA real ni un `full` IST. No se inicia V5.1. Consolida `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md`, `docs/V5/V5_0_R2_CONTRACT_VALIDATION.md` y `docs/V5/V5_0_R2A_CONTRACT_CORRECTIONS.md`. Donde R1 y R2A difieren, **R2A prevalece**, tal como exige el prompt de esta ronda; R2 se cita como evidencia empírica de soporte, no como fuente de decisión independiente.

## EXECUTIVE SUMMARY

El contrato de arquitectura de V5.0 queda consolidado sin `CONTRACT_CONFLICT` abiertos entre D-01…D-16. Las cuatro correcciones de R2A (identidad, cobertura de evidencia, observabilidad por sidecar, `EvidenceReference` como unión etiquetada) quedan incorporadas como texto final, no como enmiendas pendientes de aplicar. El modelo normalizado, el contrato de adapter, la frontera de persistencia/cache, el contrato de proyección, el contrato Template/Profile/Renderer, el contrato de provider, la frontera runtime/tooling, la observabilidad, el future-proofing de incremental/cache, la segmentación y la frontera Approval/Canonical quedan todos consolidados en una única versión final, coherente entre sí. Se fija la decisión Opción A para los 4 tests rojos como decisión final (sin aplicarla). Se definen los PRE-V5.1 GATES y el alcance exacto (in/out-of-scope) de V5.1. Con este documento, V5.1 puede comenzar sin redefinir identidad, `EvidenceReference` ni el modelo normalizado — sujeto a que se cumplan los PRE-V5.1 GATES, en particular la aplicación de la Opción A y una suite verde, que quedan pendientes de una ronda separada y de aprobación humana.

## FINAL D-01..D-16 MATRIX

| D | Estado final | Resumen consolidado |
|---|---|---|
| D-01 | `VIABLE_WITH_CONSTRAINTS` | Compatibilidad en capas (opción C): `index/*.json` byte-idéntico a V4.3 (salvo `repository.json.duration_seconds` y timestamps); `documentation/`, `ai_context/`, `consumer_projection/` con equivalencia semántica; modelo normalizado interno sin obligación de forma V4.3. Constraints empíricos confirmados por R2: serialización exacta (`json.dumps(sanitize_data(data), indent=2, ensure_ascii=False)` vía `atomic_write_text`), CRLF de plataforma, orden de claves por plantilla fija por índice (no `sort_keys` en la proyección legacy), orden de entidades = orden de emisión (no derivable de ID/ruta en varios índices), `null`/`[]` explícitos preservados, `evidence_count` persistido y no recomputado. |
| D-02 | `RESOLVED` (amended por R2A) | Ver FINAL IDENTITY CONTRACT. `EP/EVB/FLOW/DAO/SP/SQL/PATH` preservados como identidad V5 (0 colisiones medidas en IST); `PAR/CALL/UNRES` degradados a `legacy_ref` (colisiones reales 5/27/25); `Project/Component/ExternalDependency/Call` reciben IDs V5 nuevos (`PRJ-/CMP-/XDP-/CAL-`); `UnresolvedBoundary` recibe identidad V5 derivada de `path_id`; `id_unique_per_kind` acotado a los kinds con identidad real; `EntryPoint → FunctionalFlow = 1:0..1`. |
| D-03 | `VALIDATED_WITH_CONSTRAINTS` | Persistencia propia en `evidence/` (particionada) que además alimenta las proyecciones legacy. Formato físico recomendado: JSONL UTF-8/LF particionado por tipo de entidad, orden de emisión V4.3 preservado, `EVIDENCE_MANIFEST.json` con SHA-256 por partición. Constraint satisfecho: el store cubre las entidades completadas por D-02/DR-R2-02 (ver FINAL NORMALIZED EVIDENCE CONTRACT). |
| D-04 | `VALIDATED_WITH_CONSTRAINTS` | `index/` es legacy compatibility projection de `evidence/`, no evidencia canónica. Round-trip `resolvers → evidence/ → index/` byte-idéntico, viable de extremo a extremo una vez incorporada la tabla de entidades completa (D-02/R2A) y preservado el orden propio de las vistas derivadas (`dependencies`, `functional_dependencies`, `flow_unresolved`). |
| D-05 | `VALIDATED` | Cache (V5.3) ≠ evidencia: descartable, nunca fuente de verdad, su ausencia no cambia ningún resultado. Sin campos requeridos en evidence. |
| D-06 | `VALIDATED_WITH_CONSTRAINTS` | `state ∈ {confirmed, inferred, unresolved}` obligatorio en entidades con confianza; solo un resolver determinista con evidencia citada promueve `unresolved → inferred/confirmed`, registrando `promotion_basis` como unión `EvidenceReference` (D-02/DR-R2-04). Adapters, templates, renderers, proyecciones e IA no pueden cambiar `state`. V4.3 usa `confidence` con solo `{confirmed, unresolved}` real (ningún `inferred` observado en IST); `state` es el renombre con proyección inversa a `confidence`. |
| D-07 | `VALIDATED_WITH_CONSTRAINTS` | Template = presentación, Profile = selección, Renderer = formato; invariante `template_truth_invariance` comprobable sobre datos reales (3 flows de R2: trivial, rico, unresolved). La verificación post-render de refs `CALL-` gana resolubilidad al tratarse ahora como `legacy_ref` explícito en vez de identidad ambigua (DR-R2-01/04). |
| D-08 | `VALIDATED` | Profile `ai-context` define qué evidencia/nivel de detalle entra; presupuesto/empaquetado (`select_flow_ids`, `AiProjectionBuilder.package`, `measure_request_payload`) siguen siendo lógica determinista propia de la proyección IA, no de templates. Sin cambios a budgets/prompts en V5.0–V5.2. |
| D-09 | `VALIDATED_WITH_CONSTRAINTS` | `documentation/` V4.3 se reexpresa como default templates (`human-technical` ≈ `technical_documentation_renderer`; `human-functional` ≈ `human_flow_documentation`) en V5.2, manteniendo rutas V4.3 como default. `technical_documentation_renderer.py` (1222 líneas) sigue siendo el riesgo principal de equivalencia semántica. |
| D-10 | `VALIDATED_WITH_CONSTRAINTS` | Ver FINAL PROVIDER CONTRACT. Ninguna brecha identificada exige tocar evidence/selection. `GeminiProvider` = isolate hasta V5.5. |
| D-11 | `VALIDATED_WITH_CONSTRAINTS` | Ver FINAL RUNTIME/TOOLING BOUNDARY. Separación viable; solo `router.py` importa `readiness` a nivel de módulo. |
| D-12 | `RESOLVED` (amended por R2A) | Ver FINAL OBSERVABILITY CONTRACT. `RUN_SUMMARY.json` permanece intacto y byte-determinista (3 tests vigentes protegidos sin modificación); observabilidad emitida en `RUN_OBSERVABILITY.json`, sidecar aditivo fuera de D-01. |
| D-13 | `RESOLVED` | Ver TEST BASELINE DECISION. 4 fallos reproducidos y clasificados; Opción A fijada como decisión final, no aplicada todavía. |
| D-14 | `VALIDATED_WITH_CONSTRAINTS` | Campos de cache caben sin breaking change (fingerprint, versiones, reverse index); `files.json` V4.3 no tiene `sha256` (coste de I/O nuevo, a medir en V5.3). |
| D-15 | `VALIDATED_WITH_CONSTRAINTS` | Campos de segmentación suficientes para V5.6; invariantes explicitadas incluyendo `included ∩ omitted = ∅` (necesaria, no derivable solo de la unión). `functional_flows.json` V4.3 no tiene `path_ids` (derivable de `functional_paths.flow_id`). |
| D-16 | `VALIDATED` | `Evidence → Proposal → HumanDecision → CanonicalKnowledge` con stores separados; V5.1 no mezcla; proposals ya referencian IDs de evidencia (refs `entity`, DR-R2-04). |

Ningún `CONTRACT_CONFLICT` queda abierto. `D-02` y `D-12` son las únicas decisiones cuyo texto final difiere del original de R1 (enmendadas por R2A); el resto de D-01…D-16 se consolida sin cambio de fondo respecto a R1, solo con las referencias cruzadas que R2A añadió.

## FINAL NORMALIZED EVIDENCE CONTRACT

### Reglas generales (sin cambios respecto a R1)

Campos comunes obligatorios: `id` (V4.3 preservado donde aplique, o ID V5 nuevo — D-02), `kind`, `schema_version`, `state` (si porta confianza, D-06), `provenance` (lista de `EvidenceReference`, ≥1 salvo `SourceArtifact` raíz), `adapter` (`{id, version}`). Campos comunes opcionales: `labels`, `extensions` (namespaced por adapter; el core nunca lee `extensions`). Serialización: JSON UTF-8, claves ordenadas en persistencia canónica de `evidence/`, orden de emisión documentado y preservado por entidad, sin timestamps en el contenido de evidencia, paths POSIX relativos al root escaneado (o la forma original si D-01 lo exige para la proyección), sin secretos. Neutralidad de nombres: `Component` (no WebForm/Page), `EntryPoint.trigger_kind` libre del adapter, `DataOperation.store_kind`/`operation_kind`, `ExternalDependency`, `Project`.

### Lista final mínima de conceptos

| Concepto | Clasificación | Notas de consolidación |
|---|---|---|
| `SourceArtifact` | core entity | `SRC-`+SHA-256(path posix) (nuevo); ID V4.3 de archivo si existía. `sha256` es dato nuevo (V4.3 solo tenía `size`). |
| `Solution` | core relation | Agrupación `.sln` mínima en el core (`Project.member_of`, DR-R2-02); resto del `.sln` (type_guid, guid) en `extensions["vbnet-webforms-oracle"]`. |
| `Project` | core entity | ID V5 nuevo `PRJ-` (D-02/DR-R2-01); clave natural = path normalizado (259/259 únicos). |
| `Component` | core entity | ID V5 nuevo `CMP-`; clave natural = kind + source artifact + name + discriminador determinista (1 duplicado real conocido: `cc\cc\ccTMP.vb`/`ccRma1`). Incluye la variante lógica/partial (`logical_symbols`, DR-R2-02): `partial: bool`, `parts[]`. |
| `Method`/`MethodReference` | core entity (referencia de nodo) | Nueva; reemplaza el texto sin ID `proyecto::clase.metodo` de `FunctionalPath.nodes[]`; referencia tipada a `component_id` + `method_name` (o `MethodReference` estructurado cuando haya sobrecarga). |
| `EntryPoint` | core entity | `EP-` preservado (0 colisiones); `trigger_kind`, `handler_ref`, `state`; inicia `FunctionalFlow` en cardinalidad **`1:0..1`** (D-02, corregido desde `1:1`). |
| `EventBinding` | core entity | `EVB-` preservado (0 colisiones); entidad de primera clase (DR-R2-02), no fusionada con `EntryPoint`; el detalle WebForms va a `extensions`. |
| `Call` | core entity | ID V5 nuevo `CAL-`; clave natural = source artifact + containing symbol + line + expression + duplicate ordinal determinista (no basado en orden no determinista; 1 383 tuplas duplicadas medidas en R2). `Call.owner_entry_point_id` opcional cubre `entry_points.outgoing_calls[]` (DR-R2-02, core relation). |
| `Instantiation` | core entity | Nueva (DR-R2-02); `type_name`, `variable_name`, `containing_symbol_ref`, `resolved_type_ref?`; origen de la relación `InstantiatesClass`. |
| `DataOperation` | core entity | `DAO-` preservado (0 colisiones); `operation_kind`, `store_kind`, `target`, `state`; `target=unknown ⇒ unresolved`. |
| `DataObject` | core entity | Nueva (DR-R2-02); cubre `SP-` (stored procedure) y `SQL-` (sql operation), ambos preservados con 0 colisiones; nodo terminal de `FunctionalPath`. |
| `DataParameter` | core entity (sin identidad canónica propia) | Entidad hija de `DataOperation.parameters[]`; `PAR-` viaja como `legacy_ref`, no como `id` (D-02/DR-R2-01: 5 colisiones/74 633). |
| `ExternalDependency` | core entity | ID V5 nuevo `XDP-`; clave natural = tipo + source + target + metadata mínima estable. |
| `FunctionalPath` | core entity | `PATH-`+SHA-256 preservado (0 colisiones); `entry_point_id`, `nodes[]`, `relation_types[]`, `terminal_type`, `terminal_target`, `state`; id = hash canónico, no cambia. |
| `FunctionalFlow` | core entity | `FLOW-` preservado (0 colisiones); `entry_point_id`, `path_ids[]`, `state`, `summary_counts`; campos de segmentación opcionales desde V5.1 (D-15). |
| `FlowGraph` | core entity (embebido en `FunctionalFlow`) | Nueva (DR-R2-02); `nodes[]`, `edges[]`, `terminal_operations[]`; no derivable solo de `FunctionalPath` (confirmado empíricamente por R2). |
| `UnresolvedBoundary` | core entity | Identidad V5 derivada de forma estable de `path_id` (+ boundary type/target si hace falta), no de `UNRES-` (25 colisiones descartadas como identidad, D-02/DR-R2-01); vista filtrada de `FunctionalPath` con orden propio (`flow_unresolved` ≠ orden de `functional_paths`, verificado en R2). `state` siempre `unresolved`; entidad de primera clase, no un warning. |
| `EvidenceReference` | core (estructural, unión etiquetada) | Ver FINAL EVIDENCE REFERENCE CONTRACT. |
| `ScanSummary` | derived projection | Nueva (DR-R2-02); deriva de `EVIDENCE_MANIFEST.source_snapshot`; cubre `repository.stats`/`repository.ignored`. `repository.duration_seconds` es **legacy-only field**, fuera de `evidence/`, excluido de D-01. |

### Vistas/relaciones derivadas (no evidencia primaria adicional)

`index/` (proyección de compatibilidad completa, D-04), `dependencies` (derived projection; orden propio persistido, no recomputable por clave simple), `functional_dependencies` (derived projection; orden propio a fijar en V5.1), `flow_unresolved` (derived projection; vista filtrada de `FunctionalPath` con orden propio), `flow_summary` (derived projection; recalculable), `logical_symbols` (pasa a `core entity`, parte de `Component`), `outgoing_calls` (pasa a `core relation`, `Call.owner_entry_point_id`).

### Adapter extensions (adapter de referencia `vbnet-webforms-oracle`)

`Import` (VB `Imports`, DR-R2-02), `ConfigurationEntry` (`.config`/`appSettings`/`connectionStrings`, DR-R2-02), directivas/markup/eventos WebForms, cualificación de símbolos VB.NET, `.vbproj`/`.sln` (`TargetFrameworkVersion`, referencias, GUIDs), provider/`direction`/`CommandType`/verbos de transacción Oracle/ADO.NET.

### Confirmación de cobertura

Ningún grupo de campos de `index/*.json` V4.3 queda sin destino. Los 12 grupos identificados como `GAP` por R2 (`solutions`, `logical_symbols`, `outgoing_calls`, `EVB-` como entidad propia, `instantiations`, `imports`, `SP-`/`SQL-`, grafo del flow, `dependencies`, `functional_dependencies`, `configuration`, `repository`) quedan clasificados arriba como core entity, core relation, adapter extension, derived projection o legacy-only field, cerrando el criterio "todo campo V4.3 tiene destino" (acceptance test `all_v4_3_fields_have_destination`).

## FINAL IDENTITY CONTRACT

| Entity | ID prefix | Legacy preserved? | Canonical V5 identity? | legacy_ref? | Natural key | Collision rule |
|---|---|---|---|---|---|---|
| `EntryPoint` | `EP-` | Sí | Sí | No | — (ID ya persistido en V4.3) | `id_unique_per_kind`; 0 colisiones medidas en IST (12 662/12 662) |
| `EventBinding` | `EVB-` | Sí | Sí | No | — | `id_unique_per_kind`; 0 colisiones medidas (12 662/12 662) |
| `FunctionalFlow` | `FLOW-` | Sí | Sí | No | — | `id_unique_per_kind`; 0 colisiones medidas (12 642/12 642) |
| `DataOperation` | `DAO-` | Sí | Sí | No | — | `id_unique_per_kind`; 0 colisiones medidas (20 082/20 082) |
| `DataObject` (SP) | `SP-` | Sí | Sí | No | — | `id_unique_per_kind`; 0 colisiones medidas (5 389/5 389) |
| `DataObject` (SQL) | `SQL-` | Sí | Sí | No | — | `id_unique_per_kind`; 0 colisiones medidas (3/3) |
| `FunctionalPath` | `PATH-` | Sí (SHA-256 ya) | Sí | No | — | `id_unique_per_kind`; 0 colisiones medidas (170 020/170 020) |
| `Project` | `PRJ-` (nuevo) | No (nunca existió ID V4.3 estable) | Sí | No | path normalizado | SHA-256 completo sobre clave natural; 259/259 rutas únicas verificadas |
| `Component` | `CMP-` (nuevo) | No | Sí | No | kind + source artifact + name + discriminador determinista | SHA-256 completo; 1 duplicado real conocido `(file, name, kind)` requiere el discriminador |
| `ExternalDependency` | `XDP-` (nuevo) | No | Sí | No | tipo + source + target + metadata mínima estable | SHA-256 completo sobre clave natural |
| `Call` | `CAL-` (nuevo) | No (`CALL-` era transitorio, no persistido) | Sí | Sí (`CALL-` se conserva como `legacy_ref`) | source artifact + containing symbol + line + expression + duplicate ordinal determinista | SHA-256 completo; `CALL-` descartado como identidad (27 colisiones + 1 383 duplicados de tupla medidos en IST) |
| `UnresolvedBoundary` | derivado de `path_id` (nuevo esquema) | No (`UNRES-` no era identidad fiable) | Sí | Sí (`UNRES-` se conserva como `legacy_ref`) | `path_id` + boundary type/target cuando sea necesario | `UNRES-` descartado como identidad (25 colisiones medidas); `path_id` es único (162 914/162 914) |
| `DataParameter` | — (sin ID canónico V5) | No | No | Sí (`PAR-` se conserva como `legacy_ref`) | posición determinista dentro de `DataOperation.parameters[]` | `PAR-` descartado como identidad (5 colisiones/74 633 medidas) |

Reglas finales:

- No se reintroduce ninguna identidad V4.3 inexistente: `Project`, `Component`, `ExternalDependency`, `Call`, `UnresolvedBoundary`, `DataParameter` nunca usan un "ID V4.3" porque nunca tuvieron uno estable.
- `PAR-`, `CALL-`, `UNRES-` nunca se usan como identity key V5 en ningún contrato, invariante o test nuevo; solo aparecen como `legacy_ref`.
- Ningún ordinal de desambiguación se basa en orden de iteración no determinista; deriva siempre de una clave estable ya presente en la evidencia.
- `id_unique_per_kind` se exige solo sobre los kinds con identidad real: `EP, EVB, FLOW, DAO, SP, SQL, PATH, PRJ, CMP, XDP, CAL`, y sobre la identidad de `UnresolvedBoundary`.
- `EntryPoint → FunctionalFlow = 1:0..1` (20 EntryPoints `unresolved` sin flow, medido en IST).

## FINAL EVIDENCE REFERENCE CONTRACT

Unión etiquetada por `ref_type`, consolidada de DR-R2-04, sin cambios respecto a R2A:

```text
entity        {ref_type: "entity", entity_kind, entity_id}
source        {ref_type: "source", source_id, line?, excerpt?}
source_span   {ref_type: "source_span", source_id, start_line?, start_column?, end_line?, end_column?}   (reservado, no requerido para V4.3)
textual       {ref_type: "textual", text, origin?}
```

`legacy_ref` (campo opcional, no un `ref_type` propio): preserva `CALL-`, `PAR-`, `UNRES-` u otra referencia legacy no única.

Reglas finales:

- `promotion_basis` y `provenance` usan esta unión.
- Las **proposals usan exclusivamente refs `entity`** para grounding canónico (consistente con D-16); los subtipos `source`/`source_span`/`textual` no sirven de base a una proposal.
- Las referencias legacy ambiguas se conservan vía `legacy_ref` pero nunca cuentan como identidad única ni como `ref_type: "entity"`.
- **Una referencia rota debe detectarse explícitamente** por el validador (`entity_id` que no resuelve, `source_id` inexistente) — nunca se ignora en silencio.
- **No se inventan columnas para V4.3**: `source_span` queda reservado hasta que un extractor real (V5.4+) produzca `start_column`/`end_column`; V4.3 solo tiene línea.

## FINAL ADAPTER CONTRACT

Sin cambios de fondo respecto a R1; consolidado aquí por completitud. Un adapter declara `{adapter_id, adapter_version, source_kinds[], schema_version_target}` y expone: (1) source discovery (root + excludes → `SourceArtifact[]`, sin escribir en el repo legacy); (2) extraction (por artefacto → hechos crudos con `source_span`, hoy siempre sin columna real); (3) technology-specific normalization (hechos → `Component`, `EntryPoint`, `Call`, `Project`, `ExternalDependency`, `Instantiation` con `extensions` namespaced); (4) database-specific normalization (hechos de acceso a datos → `DataOperation`/`DataObject`/`DataParameter` + `ExternalDependency` de tipo store; puede ser un adapter DB distinto del de lenguaje, composición prevista en V5.4).

El resolver de flows (core) consume solo entidades normalizadas y produce `FunctionalPath`/`FunctionalFlow`/`FlowGraph`/`UnresolvedBoundary`.

Un adapter NO puede: interpretar significado de negocio; asignar `confirmed` sin evidencia determinista citada (D-06); canonicalizar; llamar a IA/red; escribir fuera de su salida; leer credenciales; leer `docs/`, `prompts/`, `tests/`, `PROJECT_STATE.json`; producir IDs sin cumplir el FINAL IDENTITY CONTRACT; modificar el legacy source.
Un adapter DEBE: entregar provenance por entidad (como `EvidenceReference`), orden determinista, reporte de errores de extracción como `UnresolvedBoundary`/errores estructurados, y ser idempotente.

**Adapter de referencia `vbnet-webforms-oracle`:** envuelve `extractors/*` y `analysis/{call,web_entry,database}_resolver` actuales sin cambiar su lógica; debe reproducir el baseline IST (D-01). Mapeo confirmado: `vbnet_extractor/call_extractor` → `Component/Call/Instantiation`; `webforms_extractor/web_event_extractor/web_entry_resolver` → `Component/EntryPoint/EventBinding`; `vbproj/solution/webconfig_extractor` + `dependency_resolver` → `Project/ExternalDependency/Solution/ConfigurationEntry`; `database_extractor/_database_*` + `database_resolver` → `DataOperation/DataObject/DataParameter`.

## FINAL PERSISTENCE/CACHE BOUNDARY

Sin cambios de fondo respecto a R1 (D-03, D-05):

- **Schema version:** `evidence_schema_version` semver (`MAJOR.MINOR`) en cada partición y en `EVIDENCE_MANIFEST.json`. MINOR = campos opcionales nuevos; MAJOR = cambio incompatible (requiere Decision Record).
- **Stage version:** cada stage declara `stage_version`, registrado en el manifest.
- **Source snapshot:** hash agregado (SHA-256 sobre lista ordenada de `path:sha256` de `SourceArtifact`).
- **Invalidation contract:** una partición es válida solo si coinciden `evidence_schema_version`, `stage_version` de su productor y los fingerprints de sus entradas. Ante duda → recomputar.
- **Evidence vs projection:** *evidence* = `evidence/` (persistida, versionada, con manifest). *Projection* = `index/`, `documentation/`, `ai_context/`, `consumer_projection/`, `RUN_SUMMARY.*` (regenerable sin reanalizar; declara `derived_from`).
- **Formato físico recomendado (medido en R2):** JSONL UTF-8/LF particionado por tipo de entidad, orden de emisión V4.3 preservado como requisito de D-01, más `EVIDENCE_MANIFEST.json` con SHA-256 por partición. Compacto ahorra ~25% sobre pretty-print; particiones razonables de ~32–64 MB. Evita duplicación entre `flow_unresolved`/`functional_paths` y `functional_dependencies`/`dependencies` marcándolas `derived projection` en vez de persistirlas dos veces como evidencia primaria.
- **Cache (V5.3):** vive en `<output>/.cache/` o directorio configurado, descartable, nunca fuente de verdad; su ausencia no cambia ningún resultado.

## FINAL PROJECTION CONTRACT

| Salida | Rol | Proyector | Garantía |
|---|---|---|---|
| `evidence/` | **canonical evidence** | (persistencia directa de los stages de análisis) | fuente de verdad interna; versionada, con `EVIDENCE_MANIFEST.json` |
| `index/` | **legacy compatibility projection** | `LegacyIndexProjector` | byte-idéntico V4.3 (D-01) |
| `documentation/` | **human presentation** | Profiles `human-functional`/`human-technical` + Template + Renderer(md) | equivalencia semántica; rutas V4.3 por defecto |
| `ai_context/` | **AI-facing projection** | Profile `ai-context` + proyector | semántica V4.3; sin budget nuevo (D-08) |
| `consumer_projection/` | **consumer projection** | `ConsumerProjector` | schema V4.3 estable, aditivo |
| `proposals/` | **AI proposal output** | stage IA opcional sobre `ai_context` | pendientes; refs `entity` verificables (D-16, DR-R2-04) |

Reglas: una proyección nunca añade evidencia ni cambia `state`; si omite entidades lo declara (`omitted_*`, conteos); toda proyección lleva `derived_from`. `index/` es compatibility projection (D-04), no evidencia canónica.

## FINAL TEMPLATE/PROFILE/RENDERER CONTRACT

- **Template = presentación:** redacta y ordena bloques a partir de entidades seleccionadas por un Profile; puede usar `extensions` pero no puede crear/alterar entidades, refs, `state` ni relaciones.
- **Profile = selección:** `{profile_id, profile_version, audience, detail_level ∈ {summary, flow, evidence}, language, include: {entity_kinds, states, scopes}, evidence_appendix, partitioning}`. Solo elige qué entra y con qué detalle.
- **Renderer = formato:** `{renderer_id, format}` (md, json, …); sin lógica de selección ni de contenido.
- **Perfiles mínimos:** `human-functional` (audiencia funcional, ES por defecto, summary-first, unresolved agrupado por causa), `human-technical` (apéndice de evidencia con refs), `ai-context` (selección/empaquetado según D-08).
- **Invariante de verdad `template_truth_invariance`:** dos templates sobre la misma evidencia ⇒ mismos IDs citados válidos, refs, `state`, relaciones y `UnresolvedBoundary`. Comprobada conceptualmente en R2 sobre 3 flows reales (trivial, rico con 146 refs `CALL-`, unresolved); la resolubilidad de esas refs mejora con DR-R2-01/04 (`CALL-` como `legacy_ref` explícito).
- **Versioning y cache key:** `projection_cache_key = SHA-256(evidence_snapshot | profile_id@version | template_id@version | renderer_id@version | language)`.
- **Fallback:** template custom que falla validación/render → `TEMPLATE_ERROR` estructurado; usa el default si `fallback=default`; nunca documentación parcial silenciosa.

## FINAL PROVIDER CONTRACT

Contrato final previsto para V5.5, sin cambios de fondo respecto a R1/R2:

`LLMProvider` (ABC) exige: `generate`, `structured_generate(request, schema) -> LLMResponse` (subido al ABC; hoy solo en implementaciones, con `UNSUPPORTED_CAPABILITY` si `structured_output=False`), `capabilities()` (`context_window`, `max_output_tokens`, `structured_output`, `json_mode`, `system_instruction`, `temperature_control`, `streaming`, `tool_use`), `model_info`, `close()`/context manager idempotente (hoy inexistente; el orquestador nunca lo invoca — gap real a cerrar en V5.5). `timeout_s` en config; `RATE_LIMITED` con `retry_after` opcional (hoy nadie lo produce — gap real); retry solo si el provider declara `retryable`, política en el orquestador. Estados: `SUCCESS, CONTEXT_TOO_LARGE, INVALID_STRUCTURED_OUTPUT, PROVIDER_ERROR, TIMEOUT, RATE_LIMITED, UNSUPPORTED_CAPABILITY` + existentes. Presupuesto: el gate de tamaño lo hace el orquestador sobre `measure_request_payload`, previo a cualquier llamada. Sanitización central (hoy duplicada en `copilot.py`, a consolidar en V5.5). `credential_source` por referencia únicamente. Import lazy del SDK del vendor. `ProviderRegistry` con factories registrables por `provider_type` en vez de `if` por tipo, `FAKE` siempre disponible. `GeminiProvider` = isolate (`providers/experimental/` o `UNREGISTERED`) hasta que V5.5 lo complete o retire.

**Confirmado (R2):** `orchestration/ai_interpretation.py` usa solo `structured_generate` + `capabilities()` + campos de `LLMResponse` + `measure_request_payload`. Todo cabe en el contrato. **Ninguna brecha exige tocar evidence ni selection.**

## FINAL RUNTIME/TOOLING BOUNDARY

| Módulo | Clasificación | Justificación |
|---|---|---|
| `knowledge.readiness` (+ `_readiness_*`), subcomando `readiness` | tooling de desarrollo | lee `codex/V3/...` y `output/LEVANTAMIENTO_*`; único punto de la cadena importado desde `main` (`router.py:20`, import a nivel de módulo) |
| `knowledge.closure.*` (`baseline_report`, `manifest_report`, `artifact_hashes`, `maintainability`) | tooling de desarrollo | lee `PROJECT_STATE.json`, `docs/V4/`, baselines; sin importadores, ya desacoplado |
| `documentation.human_review`, `documentation.second_review` | legacy congelado | escriben/leen `codex/V3`; importados por `readiness` (`EXTERNAL/PARTIAL/RESOLVED`) |
| `documentation.{generator, hierarchical, resume, systematic, consistency_run}`, `analysis.targeted_exhaustion`, `knowledge.classification.catalog`, `knowledge.projection.{contract_report, example_report, rules}`, `knowledge.domain.enums`, `llm/copilot_pilot.py` | legacy congelado (V3, acoplados a Copilot vía `asyncio.run(discover_model())`) | fuera del pipeline `full`; retiro en fase posterior (V5.9/V6) |
| Resto de `knowledge/*` (canonical, approval, proposals, plugin_projection, provenance, …) | runtime productivo | necesarios para proposals/approval (D-16); evolución en V5.7 |
| `main.py` + `legacy_documenter/` (excluyendo lo anterior) | runtime productivo | frontera formal de la distribución limpia V5 |

**Frontera formal:** ningún módulo empaquetado del runtime lee `docs/`, `prompts/`, `tests/`, `PROJECT_STATE.json`, `governance/`, `codex/`, `output/` del repo de desarrollo. `router.py` no debe importar `readiness` a nivel de módulo (import diferido o subcomando de tooling). Verificación automatizable: (a) grep/AST de rutas prohibidas bajo el paquete runtime; (b) ejecutar `analyze/full/output-manifest` desde la distribución construida aislada. Sacar `readiness/closure/human_review/second_review` de la distribución limpia no rompe `analyze/full/output-manifest`; es un cambio de CLI que debe declararse y aprobarse aparte (no en esta ronda).

## FINAL OBSERVABILITY CONTRACT

`RUN_SUMMARY.json` permanece **compatible V4.3, sin cambios**: mismo conjunto exacto de 11 claves, sin timestamps, byte-determinista entre runs equivalentes (protege los 3 tests vigentes identificados por R2).

`RUN_OBSERVABILITY.json` es un sidecar aditivo, no determinista, generado junto a `RUN_SUMMARY.json` pero explícitamente **fuera de D-01**.

| Campo | Clase |
|---|---|
| `stage_started_at` | required |
| `stage_finished_at` | required |
| `duration_ms` | required |
| `input_count` | required |
| `output_count` | required |
| `cache_hit` | optional (desde V5.3; `null` antes) |
| `cache_miss` | optional (desde V5.3; `null` antes) |
| `provider_calls` | optional (solo stages IA) |
| `payload_estimated_tokens` | optional (solo stages IA) |
| `peak_memory_mb` | diagnostic (best-effort, `null` si no medible) |
| `threads_alive_at_exit` | diagnostic (solo si se investiga el riesgo `PROCESS EXIT`) |

Reglas: no es evidence (sin `state`, sin `provenance`); no participa en byte-equivalence; puede faltar sin invalidar evidence; no altera exit codes (`0/1/2/4`); no contiene secretos ni contenido de fuente.

## FINAL INCREMENTAL/CACHE FUTURE-PROOFING

Solo contratos (algoritmos en V5.3, no se diseñan en esta ronda):

- **File fingerprint:** SHA-256 del contenido + tamaño en `SourceArtifact` (dato nuevo; V4.3 solo tenía `size`).
- **Adapter version / extractor version / stage version / schema version:** siempre registrados en `EVIDENCE_MANIFEST.json` (campos nuevos, no existen hoy).
- **Reverse dependency index:** `SourceArtifact → {entidades producidas}` y `entidad → {flows que la contienen}`, persistible como partición de evidencia (`evidence/reverse_index`); requiere IDs de `Call` sin ambigüedad (resuelto por D-02/DR-R2-01); schema fijado en V5.1, uso en V5.3.
- **Flow invalidation:** unidad natural = `FunctionalFlow` (grafo por EntryPoint); el `FlowGraph` (`nodes/edges`) debe estar en evidence (DR-R2-02, ya incorporado).
- **Projection cache key / template version / profile version:** ya definidos en FINAL TEMPLATE/PROFILE/RENDERER CONTRACT; no tocan evidence.
- **Cache key (stage):** `SHA-256(stage_id@stage_version | adapter@version | fingerprints de entradas | parámetros relevantes)`.
- **Identidad y contenido:** `SRC-`+SHA-256(path) ⇒ renombrar un archivo crea un nuevo `SourceArtifact` (y cambia `EP-`, que incluye la ruta del webform en su hash); compatible con V5.3 si el fingerprint de contenido se usa como clave de reutilización de hechos de extracción, no como identidad.
- Garantía: añadir cache no cambia IDs ni schema base (D-05, D-14).

## FINAL SEGMENTATION CONTRACT

`FunctionalFlow` (y `FunctionalPath` donde aplique) incluye desde V5.1, como opcionales con default neutro: `parent_flow_id` (null si no es segmento), `segment_id` (`SEG-`+SHA-256; null si flow completo), `partial` (bool, default false), `included_paths[]`, `omitted_paths[]` (vacío por defecto), `evidence_refs[]`, `segment_reason` (opcional).

Invariantes finales:

```text
included ∪ omitted = parent.path_ids
included ∩ omitted = ∅
included ⊆ parent.path_ids
partial=true  ⇒ omitted != ∅
partial=false ⇒ omitted = ∅
```

Reglas: un segmento nunca redefine el flow padre (el flow completo sigue existiendo con `path_ids` íntegros); los IDs `FLOW-` V4.3 no cambian; V5.1 solo serializa estos campos con sus defaults, sin proyectarlos en `functional_flows.json` legacy (D-01); la lógica de segmentar es V5.6.

## FINAL APPROVAL/CANONICAL BOUNDARY

Pipeline conceptual con stores y entidades separados:

```text
Evidence (evidence/) → Proposal (proposals/, PRP-) → HumanDecision (V5.7, DEC-) → CanonicalKnowledge (V5.7, CAN-)
```

`Proposal`: `evidence_refs` obligatorios (refs `entity`, DR-R2-04), `status=PENDING_…`. `HumanDecision`: `proposal_id`, `decision`, `decided_by`, `rationale`, `decided_at`. `CanonicalKnowledge`: `derived_from_decision`, `evidence_refs`.

V5.1 debe: (a) no incluir en `evidence/` ningún dato de proposal/decisión/canónico; (b) garantizar que los `evidence_refs` de una proposal apunten a IDs de evidencia, no a texto; (c) no requerir cambios en evidencia para V5.7. **Sin auto-approval ni auto-canonicalization**: `approval_surface_implementation` sigue `NOT_IMPLEMENTED` hasta V5.7.

## V4.3 → V5 MIGRATION STRATEGY

1. **V5.1:** introduce `evidence/` (con la identidad y cobertura de campos finales de este documento) y el adapter de referencia envolviendo el código actual; `index/` se proyecta desde `evidence/` (D-04). Gate: D-01 sobre fixtures + IST.
2. **V5.2:** documentación por Profile/Template/Renderer con defaults equivalentes a V4.3; nuevas rutas aditivas.
3. **V5.3:** cache/incremental sobre `evidence/` (D-05, D-14).
4. **V5.4:** adapters adicionales/DB; el resolver de flows ya solo ve entidades neutrales.
5. **V5.5:** provider contract completo, registro extensible.
6. **V5.6–V5.8:** segmentación, approval/canonical, consumer/plugin.
7. **Transición:** durante V5.1–V5.3 conviven salidas V4.3 y `evidence/`; ningún consumidor V4.3 necesita cambios. `PROJECT_STATE.json`/baselines V4.3 no se editan retroactivamente.
8. **Rollback:** cada fase es aditiva; desactivar `evidence/` deja el pipeline V4.3 intacto hasta V5.3.

## TEST BASELINE DECISION

Se incorpora la **Opción A** como decisión final (consolidada de R2/R2A, sin aplicarla en esta ronda):

1. `PROJECT_STATE.json` representa estado/historia acumulada del proyecto y puede avanzar legítimamente; no es un snapshot congelado de una fase.
2. Las invariantes históricas de una fase (p. ej. "V4 tuvo 0 llamadas reales a IA") pertenecen a los artefactos congelados de esa fase (`output/v4_r14/V4_FINAL_BASELINE.json`, cuyo test ya pasa hoy).
3. Las aserciones `provider_calls == 0`/`real_llm_calls == 0` (`tests/test_v4_r13_regression_and_security.py:740`; `tests/test_v4_r14_manuals_and_final_baseline.py:89,510`) deben dejar de evaluarse contra `PROJECT_STATE.json` vivo.
4. `test_baseline_matches_on_disk_artifact` (`tests/test_v4_r14_manuals_and_final_baseline.py:334`) debe normalizar también `provider_calls` y `real_llm_calls`, siguiendo el patrón `REG-002` ya usado para otros campos que avanzan legítimamente.
5. Los 4 tests se corregirán en una **ronda separada**, autorizada explícitamente, con `PROJECT_STATE.json` sin editar retroactivamente. **R3 no modifica tests.**

## PRE-V5.1 GATES

Antes de autorizar el inicio de V5.1, deben cumplirse explícitamente:

1. Aplicar la Opción A a los 4 tests rojos (ronda separada, autorizada explícitamente).
2. Suite completa verde (0 fallos conocidos; los 2169 tests/132 skips de R1 reejecutados y confirmados, no solo citados).
3. No editar retroactivamente `PROJECT_STATE.json` al aplicar la corrección del punto 1.
4. No quedan conflictos contractuales: la FINAL D-01..D-16 MATRIX de este documento se mantiene sin `CONTRACT_CONFLICT`.
5. Contrato R1+R2A consolidado: este documento (R3) es la versión de referencia única; cualquier cambio posterior requiere un nuevo Decision Record explícito.
6. V5.1 implementa sin redefinir identidad ni `EvidenceReference`: FINAL IDENTITY CONTRACT y FINAL EVIDENCE REFERENCE CONTRACT de este documento se toman como dados, no como punto de partida de discusión.

## V5.1 IN-SCOPE

- Normalized evidence core.
- Identity implementation (FINAL IDENTITY CONTRACT).
- `EvidenceReference` (FINAL EVIDENCE REFERENCE CONTRACT).
- Persistencia de `evidence/` (formato JSONL particionado, `EVIDENCE_MANIFEST.json`).
- Proyección legacy `index/` (D-04, round-trip byte-idéntico).
- Validación de colisiones (`id_unique_per_kind` sobre los kinds con identidad real).
- Manifest de schema/versión (`evidence_schema_version`, `stage_version`).
- Adapter de referencia como wrapper (`vbnet-webforms-oracle`, sin reescribir resolvers).
- Esqueleto de `RUN_OBSERVABILITY.json` (campos `required` como mínimo).

## V5.1 OUT-OF-SCOPE

- Template engine completo (V5.2).
- Cache incremental (V5.3).
- Adapters multi-tecnología (V5.4).
- Implementación genérica de provider (V5.5).
- Lógica rica de segmentación (V5.6).
- Approval surface (V5.7).
- Plugin runtime (V5.8).

## RISKS

1. El "duplicate ordinal determinista" de `Call` (`CAL-`) y el discriminador de `Component` (`CMP-`) no se verificaron a escala completa de IST; V5.1 debe correr el detector de colisiones sobre ambos antes de cerrarse.
2. El orden propio de `dependencies`/`functional_dependencies` como `derived projection` no es recomputable por clave simple (confirmado en R2); si V5.1 lo omite, D-01 podría romperse para esos dos índices.
3. `RUN_OBSERVABILITY.json`, al no participar en D-01, podría divergir de forma no controlada entre runs si V5.1 no documenta al menos su estabilidad de forma (no de valor).
4. Referencias `CALL-`/`UNRES-` ambiguas (18 + 396, medidas en R2) siguen sin resolverse individualmente; quedan correctamente clasificadas como `legacy_ref` no único, pero la ambigüedad subyacente en los datos legacy persiste.
5. `technical_documentation_renderer.py` (1222 líneas) sigue siendo el mayor riesgo de equivalencia semántica para D-09/V5.2.
6. `sha256` de archivos no existe en V4.3; el coste de SCAN (lectura completa de 15 151 archivos) no está medido; puede afectar el presupuesto de tiempo de V5.1/V5.3.
7. Riesgo intermitente `test_deterministic_run_then_ai_enabled_rerun_same_output` (V4.2-R6): no reproducido desde entonces, pero sigue como trigger de investigación obligatorio ante cualquier recurrencia.
8. `PROCESS EXIT` sigue `NOT_REPRODUCED`; sin nueva evidencia el estado no cambia.
9. El PRE-V5.1 GATE 2 (suite completa verde) depende de una ronda de corrección de tests que R3 no autoriza a ejecutar; hasta que esa ronda se apruebe y complete, V5.1 no puede iniciarse formalmente aunque el resto de gates se cumplan.

## DEFERRED ITEMS

- Corrección física de los 4 tests rojos (Opción A) → ronda posterior, autorizada explícitamente, `PROJECT_STATE.json` sin editar retroactivamente.
- Verificación de `id_unique_per_kind` sobre `CAL-`/`CMP-` a escala completa de IST → V5.1.
- Formato físico definitivo de `evidence/` (confirmación JSONL particionado con medición a escala completa) → V5.1.
- `source_span` con columnas reales → no antes de V5.4.
- Esquema físico exacto de `RUN_OBSERVABILITY.json` → V5.1.
- Algoritmos de invalidación/propagación de cache → V5.3.
- `close()`, registro extensible de providers, consolidación del sanitizador → V5.5.
- Destino final de `GeminiProvider` (completar/retirar) → V5.5.
- Segmentación real → V5.6; Approval/Canonical → V5.7; contrato Plugin → V5.8.
- Retiro de módulos V3 legacy congelados → V5.9/V6.
- Creación de cualquier prompt de ronda siguiente (incluido el de corrección de tests o el de inicio de V5.1) → requiere aprobación humana explícita; no se crea en esta ronda.

## FILES READ

`CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`, `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md`, `docs/V5/V5_0_R2_CONTRACT_VALIDATION.md`, `docs/V5/V5_0_R2A_CONTRACT_CORRECTIONS.md`, `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`, `prompts/V5_0/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE_PROMPT.md`.

## FILES MODIFIED

- Creado: `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`.
- Ningún otro archivo del repositorio modificado.
