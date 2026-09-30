# V5.0 R1 — Architecture Contract

## STATUS

`V5_0_R1_CONTRACT_READY`

Ronda de diseño/documental. No se modificó producción, tests, CLI, prompts, providers ni `PROJECT_STATE.json`. Base: `docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md`. Las decisiones D-01…D-16 son la fuente de verdad para R2–R4 y V5.1–V5.9; cambiarlas requiere un nuevo Decision Record explícito.

Evidencia adicional consultada en esta ronda (solo lectura):
- Derivación de IDs V4.3: `PATH-` usa SHA-256 sobre JSON canónico (`flow_resolver._path_id`); `EP-`, `FLOW-`, `DAO-` usan un hash polinomial `h = (h*33 + ord(c)) mod 1_000_000_007` sobre `"|".join(parts)`, formateado a 10 dígitos (`_stable_id` en `web_entry_resolver`, `flow_resolver`, `database_resolver`). Es determinista, pero con espacio de solo ~10^9 valores: **riesgo de colisión no descartado a escala IST**. Estimación de cumpleaños ≈ n²/(2N) con N≈10^9, suponiendo distribución uniforme (no verificado): EP (12 662) ≈ 0.08, FLOW (12 642) ≈ 0.08, DAO (20 082) ≈ 0.20 esperadas por tipo. Es decir, una colisión es improbable pero no despreciable; no está verificado que no exista ninguna en el índice real. Ver D-02.
- Los 4 tests rojos afirman `provider_calls == 0` / `real_llm_calls == 0` contra `PROJECT_STATE.json` vivo (`test_v4_r13…:740-741`, `test_v4_r14…:89-90, 216-217, 510-511`). `PROJECT_STATE.json` vale 1/1 desde el commit `44e2a94` (piloto real V4.3).

## EXECUTIVE SUMMARY

V5 introduce un **modelo de evidencia normalizado y neutral a la tecnología** como fuente canónica interna, persistido como artefacto propio (`evidence/`), del que se **proyectan** —sin alterarla— las salidas V4.3 (`index/`, `documentation/`, `ai_context/`, `consumer_projection/`, `proposals/`). Compatibilidad en **capas (opción C)**: proyecciones legacy `index/*.json` byte-idénticas a V4.3 sobre el mismo input; el resto (documentación, contexto IA) con equivalencia semántica de IDs/refs/estados/conteos. Los IDs V4.3 se preservan tal cual; el adapter WebForms/VB/Oracle es el adapter de referencia y produce entidades neutrales con extensiones namespaced. Templates/Profiles/Renderers cambian presentación, nunca verdad. El contrato de provider se completa y se hace registrable por configuración. `readiness/closure/human_review/second_review` salen de la distribución runtime. Se prevén desde V5.1 los campos de segmentación, cache y aprobación para evitar breaking changes. Los 4 tests rojos son **obsoletos por diseño** (asumen que `PROJECT_STATE` es un snapshot de V4-R13/R14) y se resuelven en R2 con criterio explícito, no en R1.

Las 9 decisiones abiertas de R0 → D-03 (1), D-04 (2), D-05 (3), D-13 (4), D-10 (5), D-01 (6), D-08 (7), D-14 (8), D-07/D-08 (9). Ver mapa en DECISIONS.

## DECISIONS

Formato reducido de Decision Record: cada D-xx incluye Problem / Decision / Rationale / Alternatives rejected / Compatibility / Migration / Acceptance test / Deferred. Los detalles de contratos están en las secciones siguientes.

### D-01 — Política de compatibilidad (opción C, en capas)
- **Problem:** ¿V5 exige salidas idénticas o equivalentes a V4.3?
- **Decision:** **C**. (1) *Proyecciones legacy de evidencia* (`index/*.json`, salvo campos temporales) → **byte-idénticas** a V4.3 para el mismo input. (2) *Proyecciones presentacionales/derivadas* (`documentation/`, `ai_context/`, `consumer_projection/`, `RUN_SUMMARY.md`) → **equivalencia semántica** (mismos IDs, evidence_refs, estados, conteos, orden de entidades), no byte. (3) *Modelo normalizado interno* → sin obligación de forma V4.3, solo de información: debe permitir reconstruir (1).
- **Rationale:** `index/` es lo que consumen `ai_context`, hydration y manifests históricos; congelarlo da una suite de aceptación objetiva. Congelar la prosa humana bloquearía V5.2.
- **Alternatives rejected:** A pura (impide templates); B pura (no detecta regresiones sutiles de orden/serialización).
- **Compatibility:** campos temporales excluidos de la comparación byte: `repository.json.duration_seconds` y timestamps.
- **Migration:** V5.1 debe pasar la comparación byte de `index/` en fixtures y hash-por-índice en IST antes de ser aceptada.
- **Acceptance test:** `legacy_projection_byte_equivalence` (fixtures `v2_r1_sample`, `v4_2_r3_sample`, `v4_2_r7_full_sample`) + comparación de SHA-256 por índice contra `OUTPUT_MANIFEST.json` de IST.
- **Deferred:** la default template `human-*` puede pedir opcionalmente byte-equivalencia a V4.3 (V5.2).

### D-02 — Identidad e IDs
- **Problem:** hay dos esquemas de ID (SHA-256 para `PATH`; hash polinomial de 10 dígitos para `EP/FLOW/DAO`), y el segundo puede colisionar.
- **Decision:** los IDs V4.3 se preservan **sin cambios** como `id` de la entidad normalizada (contrato con evidence_refs, proposals, hydration, consumer). V5 **no** re-deriva ni migra IDs. Se añade (a) un **detector de colisiones obligatorio** (invariante `id_unique_per_kind`) que, ante colisión, falla la validación y reporta — nunca renombra; (b) IDs **nuevos** de V5 (`SEG-`, `SRC-`, `UNR-` si aplican, `DEC-`, `CAN-`) usan SHA-256 completo sobre JSON canónico; (c) campo opcional `legacy_id_scheme` (`poly33` | `sha256`) para trazabilidad.
- **Rationale:** cambiar IDs invalida proposals, refs y consumidores; el riesgo de colisión se gestiona detectándolo, no reescribiendo historia.
- **Alternatives rejected:** migrar a SHA-256 (rompe todo); ignorar colisiones (silencioso).
- **Compatibility:** total. **Migration:** ninguna en datos; V5.1 agrega validación.
- **Acceptance test:** `ids_preserved` (mismo conjunto de IDs por tipo en IST y fixtures) + `id_unique_per_kind` (0 colisiones o fallo explícito).
- **Deferred:** decidir si colisiones detectadas en IST requieren un esquema `v2` de ID con alias (solo si el detector encuentra alguna; R2 debe ejecutarlo).

### D-03 — Frontera de persistencia
- **Problem:** ¿el conocimiento normalizado se persiste, se cachea o alimenta legacy?
- **Decision:** **c**: se persiste como artefacto propio y **además** alimenta las proyecciones legacy. Ubicación conceptual: `<output>/evidence/` (nombre distinto de `legacy_documenter/knowledge/` para no colisionar). Contenido: particiones por tipo de entidad + `EVIDENCE_MANIFEST.json` (`schema_version`, `stage_versions`, `source_snapshot`, `entity_counts`, SHA-256 por partición).
- **Rationale:** sin persistencia, V5.2 (templates) y V5.3 (incremental) tendrían que re-analizar; la frontera queda explícita: *evidence* = `evidence/`; todo lo demás = *projection* regenerable sin reanalizar.
- **Alternatives rejected:** solo cache (la cache es descartable; la evidencia no); solo `index/` como canónico (mantiene el vocabulario WebForms en el core).
- **Compatibility:** `evidence/` es aditivo; no altera output paths V4.3. **Migration:** en V5.1 se genera junto a `index/`.
- **Acceptance test:** regenerar `documentation/` y `ai_context/` desde `evidence/` sin ejecutar SCAN/EXTRACTION produce salida equivalente (D-01).
- **Deferred:** formato físico (JSONL particionado vs JSON) — a fijar en V5.1 con medición; el contrato exige particionado, no un JSON monolítico.

### D-04 — `index/` pasa a proyección de compatibilidad
- **Decision:** `index/*.json` es **legacy compatibility projection** de `evidence/`. Deja de ser evidencia canónica en V5 (sigue siendo contrato de salida V4.3). Durante V5.1 el modelo normalizado se construye **a partir de las estructuras que ya producen los resolvers** (no reescribe resolvers) y se proyecta de vuelta a `index/` con la garantía de D-01.
- **Rationale/Alternatives:** mantener `index/` canónico conserva la contaminación tecnológica (R0 riesgo 1).
- **Acceptance test:** round-trip `resolvers → evidence/ → index/` byte-idéntico.
- **Deferred:** retirada de `index/` como default (no antes de V6).

### D-05 — Cache ≠ evidencia
- **Decision:** cache (V5.3) vive en `<output>/.cache/` o directorio configurado, es descartable, nunca fuente de verdad, y su ausencia no cambia ningún resultado. Evidencia persistida (D-03) no se invalida por borrar cache.
- **Acceptance test:** salida con cache fría == salida con cache caliente (D-01).

### D-06 — Principio de no-promoción de `unresolved`
- **Decision:** `state ∈ {confirmed, inferred, unresolved}` es un campo obligatorio de toda entidad con semántica de confianza; solo un **resolver determinista con evidencia citada** puede subir `unresolved → inferred/confirmed`, y debe registrar `promotion_basis` (lista de EvidenceReference). Adapters, templates, renderers, proyecciones e IA **no pueden** cambiar `state`. Las proposals de IA llevan su propio `confidence` que nunca sobreescribe `state` de evidencia.
- **Acceptance test:** invariante `state_immutable_across_projections` y `no_promotion_without_basis`.

### D-07 — Contrato Template/Profile/Renderer (ver sección)
Template=presentación, Profile=selección, Renderer=formato; invariante de igualdad de verdad entre templates.

### D-08 — Frontera Profile vs AI projection
- **Decision:** el **Profile** `ai-context` define *qué* evidencia/nivel de detalle entra (selección declarativa); el **presupuesto y empaquetado** (`select_flow_ids`, `AiProjectionBuilder.package`, `measure_request_payload`) siguen siendo lógica determinista propia de la proyección IA y **no** pasan a templates. Un Profile puede acotar candidatos pero no el algoritmo de budget. Sin cambios a budgets/prompts en V5.0–V5.2.
- **Acceptance test:** con el profile por defecto, `ai_context/` y el paquete IA son semánticamente iguales a V4.3.

### D-09 — Migración de documentación V4.3 a templates
- **Decision:** la salida V4.3 de `documentation/` se reexpresa como **default templates** (`human-technical` ≈ `technical_documentation_renderer`; `human-functional` ≈ `human_flow_documentation`) en V5.2, manteniendo rutas de archivo V4.3 como default. Nuevos perfiles/idiomas emiten en subdirectorios de perfil sin pisar rutas V4.3.

### D-10 — Provider contract (ver sección)
ABC completo, registro por configuración, ciclo de vida, `GeminiProvider` = **isolate** (mover a `providers/experimental/` o marcar `UNREGISTERED`; no completar hasta V5.5).

### D-11 — Frontera runtime / tooling
Ver sección: `readiness`, `closure` → tooling de desarrollo; `human_review`, `second_review`, módulos V3 acoplados a Copilot → legacy congelado; retiro en V5.9+/V6.

### D-12 — Observabilidad aditiva
Campos aditivos en `RUN_SUMMARY.json` bajo clave `observability` (ver sección); lectores V4.3 no se rompen.

### D-13 — Resolución de la inconsistencia de tests
Ver TEST BASELINE RESOLUTION.

### D-14 — Contratos de cache previstos desde V5.1
Fingerprints, versiones y unidad de invalidación se incluyen en el esquema de evidencia desde V5.1 (campos ya presentes, sin lógica).

### D-15 — Segmentación prevista en V5.1
`FunctionalFlow` incluye desde V5.1 los campos de segmentación como opcionales (sección).

### D-16 — Frontera Evidence → Proposal → Decision → Canonical
Entidades y stores separados; V5.1 no mezcla (sección).

## NORMALIZED EVIDENCE CONTRACT

### Reglas generales (aplican a todas las entidades)
- **Campos comunes obligatorios:** `id` (V4.3 preservado, D-02), `kind` (nombre de entidad), `schema_version`, `state` (si la entidad porta confianza, D-06), `provenance` (lista de `EvidenceReference`, ≥1 salvo `SourceArtifact` raíz), `adapter` (`{id, version}` que la produjo).
- **Campos comunes opcionales:** `labels` (texto humano, no semántico), `extensions`.
- **`extensions`:** objeto namespaced por adapter, p. ej. `extensions["vbnet-webforms-oracle"]`. El core **nunca** lee `extensions`; solo adapters, proyecciones legacy y templates específicos. Una entidad sin extensiones es válida.
- **Serialización:** JSON UTF-8, claves ordenadas (`sort_keys`) en persistencia canónica, listas en orden determinista documentado por entidad, sin timestamps en el contenido de evidencia, paths POSIX relativos al root escaneado, sin secretos (sanitizador central).
- **Neutralidad de nombres:** `Component` (no WebForm/Page), `EntryPoint` con `trigger_kind` (valor libre del adapter, p. ej. `webforms.event`), `DataOperation` con `store_kind`/`operation_kind` (no `Oracle`/`DAO` en el core), `ExternalDependency`, `Project` (no `.vbproj`).

### Entidades

| Entidad | Identidad | Obligatorios (además de comunes) | Opcionales | Relaciones | Invariantes |
|---|---|---|---|---|---|
| `SourceArtifact` | `SRC-`+SHA-256(path relativo posix) [nuevo]; ID V4.3 de archivo si existía | `path`, `sha256`, `size_bytes`, `artifact_kind` | `language`, `encoding` | pertenece a `Project` | `sha256` reproducible; el legacy source es solo lectura |
| `Project` | ID V4.3 (`PROJECT-…`) | `name`, `root_path`, `artifact_refs[]` | `kind`, `dependencies[]` (a `ExternalDependency`/`Project`) | contiene `Component` | agrupación estable; base del particionado de docs |
| `Component` | ID V4.3 (símbolo/webform) | `name`, `component_kind`, `project_id`, `source_ref` | `parent_id`, `members[]` | contiene `EntryPoint`; emite `Call` | `source_ref` resuelve a un `SourceArtifact` |
| `EntryPoint` | `EP-…` V4.3 | `component_id`, `trigger_kind`, `handler_ref`, `state` | `trigger_label` | inicia `FunctionalFlow` (1:1 en V4.3) | ordering por id; `state` derivado de resolución |
| `Call` | ID V4.3 de call | `caller_ref`, `callee_ref` \| `callee_unresolved_target`, `state`, `evidence` | `arguments_summary` | alimenta `FunctionalPath` | si `callee_ref` ausente ⇒ `state=unresolved` |
| `DataOperation` | `DAO-…` V4.3 | `operation_kind`, `store_kind`, `target` (nombre de tabla/SP/consulta o `unknown`), `state` | `parameters[]`, `transaction_verb` | terminal de `FunctionalPath` | `target=unknown` ⇒ `unresolved`; sin SQL/credenciales en claro |
| `ExternalDependency` | ID V4.3 | `name`, `dependency_kind` | `version`, `source_ref` | referenciada por `Project` | — |
| `FunctionalPath` | `PATH-`+SHA-256 (V4.3) | `entry_point_id`, `nodes[]`, `relation_types[]`, `terminal_type`, `terminal_target`, `state` | `flow_id` | pertenece a `FunctionalFlow` | id = hash canónico de (entry_point, nodes, relations, terminal) — **no cambiar** |
| `FunctionalFlow` | `FLOW-…` V4.3 | `entry_point_id`, `path_ids[]`, `state`, `summary_counts` | campos de segmentación (ver sección) | agrupa `FunctionalPath` | `path_ids` completos y ordenados; nunca podado por una proyección |
| `UnresolvedBoundary` | ID V4.3 en `flow_unresolved` (o derivado sha256 si no existía) | `path_id`, `boundary_target`, `reason_code`, `state=unresolved` | `candidates[]` (solo si determinista) | referenciada por `FunctionalPath` | `state` siempre `unresolved`; es de primera clase, no un warning |
| `EvidenceReference` | estructural (sin ID propio): `{source_id, kind, locator}` | `entity_id`, `entity_kind` | `source_span` (línea/columna) | apunta a cualquier entidad o `SourceArtifact` | debe resolverse en el store; ref rota = fallo de validación |

### Qué pasa a extensiones/adapter (adapter de referencia `vbnet-webforms-oracle`)
- WebForms: `directives`, `codebehind`, `codefile`, `inherits`, `master_page`, `registers`, `scripts`, `stylesheets`, `markup_events`, nombres `Page_Load`/eventos de control.
- VB.NET: cualificación de símbolos, `.vb` `partial`, `Imports`.
- `.NET Framework`/`.vbproj`: `TargetFrameworkVersion`, referencias, `.sln`.
- Oracle/ADO.NET: proveedor (`Oracle`/`OleDb`), `direction` de parámetros (Input/Output/…), `CommandType`, verbos de transacción.
- El core conserva solo lo necesario para razonar (estado, referencias, terminal, conteos).

### Cómo se evita promover unresolved
D-06. Adicionalmente: los campos `state`, `promotion_basis` y `UnresolvedBoundary` viajan intactos en toda proyección; cualquier proyección que descarte un `UnresolvedBoundary` debe declararlo en `omitted_*` (ver segmentación) y en métricas.

## ID / COMPATIBILITY CONTRACT

Ver D-01, D-02. Invariantes **obligatorios** (suite de aceptación; ✓ = byte para `index/`, ≈ = semántico para el resto):

| Invariante | `index/` | documentation / ai_context / consumer / proposals |
|---|---|---|
| IDs (mismo conjunto y valores) | ✓ | ≈ (mismos IDs citados) |
| evidence_refs (existen, resuelven) | ✓ | ≈ (100 % resuelven al store/índice) |
| conteos (entry_points, flows, paths, unresolved, data_access, files) | ✓ | ≈ |
| estados confirmed/inferred/unresolved | ✓ | ≈ |
| ordering determinista de entidades | ✓ | ≈ (orden de entidades; el orden del texto puede variar por template) |
| CLI (subcomandos, flags, exit codes 0/1/2/4) | sin cambios | sin cambios |
| output paths V4.3 | sin cambios | sin cambios (los nuevos son aditivos) |
| consumer_projection (schema, particiones `parts/part-NNNNNN.json`) | n/a | ≈ (schema V4.3 estable; campos aditivos permitidos) |
| proposals (`PENDING_TECHNICAL_LEAD_REVIEW`, `technical_lead_approval=false`, `canonical_knowledge_produced=false`) | n/a | ✓ semántica idéntica |
| sin IA sin `--allow-ai-interpretation` | — | ✓ |

Cambios aditivos permitidos sin decisión nueva: campos nuevos opcionales, directorios nuevos (`evidence/`), claves nuevas en `RUN_SUMMARY.json`. Cambios **no** permitidos sin nuevo Decision Record: renombrar/eliminar campos o rutas V4.3, cambiar derivación de IDs, cambiar exit codes.

## ADAPTER CONTRACT

Un adapter declara `{adapter_id, adapter_version, source_kinds[], schema_version_target}` y expone cuatro responsabilidades:

1. **Source discovery:** dado root + excludes → `SourceArtifact[]` (hash, tipo). Sin escribir en el repo legacy.
2. **Extraction:** por artefacto → hechos crudos con `source_span`.
3. **Technology-specific normalization:** hechos → `Component`, `EntryPoint`, `Call`, `Project`, `ExternalDependency` con `extensions` namespaced.
4. **Database-specific normalization:** hechos de acceso a datos → `DataOperation` (+ `ExternalDependency` de tipo store). Un adapter de DB puede ser distinto del de lenguaje/framework (V5.4: composición adapter tecnología + adapter DB).

El **resolver de flows** (core) consume solo entidades normalizadas y produce `FunctionalPath/FunctionalFlow/UnresolvedBoundary`.

**Un adapter NO puede:** interpretar significado de negocio; asignar `confirmed` sin evidencia determinista citada (D-06); canonicalizar; llamar a IA/red; escribir fuera de su salida; leer credenciales; leer `docs/`, `prompts/`, `tests/`, `PROJECT_STATE.json`; producir IDs sin cumplir D-02; modificar el legacy source.
**Un adapter DEBE:** entregar provenance por entidad, orden determinista, reporte de errores de extracción como `UnresolvedBoundary`/errores estructurados (no excepciones silenciosas), y ser idempotente.

**Adapter de referencia `vbnet-webforms-oracle`:** envuelve `extractors/*` y `analysis/{call,web_entry,database}_resolver` actuales; no cambia su lógica. Debe reproducir el baseline IST (D-01). Mapeo: `vbnet_extractor/call_extractor` → `Component/Call`; `webforms_extractor/web_event_extractor/web_entry_resolver` → `Component/EntryPoint`; `vbproj/solution/webconfig_extractor` + `dependency_resolver` → `Project/ExternalDependency`; `database_extractor/_database_*` + `database_resolver` → `DataOperation`.

## PERSISTENCE / CACHE BOUNDARY

Ver D-03, D-05.

- **Schema version:** `evidence_schema_version` semver (`MAJOR.MINOR`), en cada partición y en `EVIDENCE_MANIFEST.json`. MINOR = campos opcionales nuevos; MAJOR = cambio incompatible (requiere Decision Record y migración).
- **Stage version:** cada stage declara `stage_version`; se registra en el manifest. Cambiar la lógica de un stage incrementa su versión.
- **Source snapshot:** hash agregado (SHA-256 sobre lista ordenada de `path:sha256` de `SourceArtifact`) — misma noción que `source_snapshot` actual de contexto/LLMRequest.
- **Invalidation contract:** una partición de evidencia es válida solo si coinciden `evidence_schema_version`, `stage_version` de su productor y los fingerprints de sus entradas. Ante duda → recomputar.
- **Evidence vs projection:** *evidence* = `evidence/` (persistida, versionada, con manifest). *Projection* = `index/`, `documentation/`, `ai_context/`, `consumer_projection/`, `RUN_SUMMARY.*`: regenerable sin reanalizar; declara `derived_from` (evidence snapshot + template/profile versions).
- **Regenerable sin reanalizar:** todo lo que no sea SCAN/EXTRACTION/resolución; los stages de IA solo se reejecutan explícitamente.

## PROJECTION CONTRACT

`evidence/` → proyectores puros (sin IO de análisis, sin IA, deterministas):

| Salida | Proyector | Garantía |
|---|---|---|
| `index/` | `LegacyIndexProjector` | byte-idéntico V4.3 (D-01) |
| `documentation/` | Profiles `human-functional`/`human-technical` + Template + Renderer(md) | equivalencia semántica; rutas V4.3 por defecto |
| `ai_context/` | Profile `ai-context` + proyector | semántica V4.3; sin budget nuevo |
| `consumer_projection/` | `ConsumerProjector` | schema V4.3 estable, aditivo |
| `proposals/` | stage IA opcional sobre `ai_context` | pendientes; refs verificables |

Reglas: una proyección nunca **añade** evidencia ni cambia `state`; si **omite** entidades lo declara (`omitted_*`, conteos); toda proyección lleva `derived_from`. `index/` **es** compatibility projection (D-04), no evidencia canónica.

## TEMPLATE / PROFILE / RENDERER CONTRACT

- **Profile** (selección, declarativo, versionado): `{profile_id, profile_version, audience, detail_level ∈ {summary, flow, evidence}, language, include: {entity_kinds, states, scopes}, evidence_appendix: bool|mode, partitioning}`. Solo elige qué entidades/campos entran y con qué detalle; no redacta.
- **Template** (presentación, versionado): `{template_id, template_version, profile_compat[], language, sections[]}`. Redacta y ordena bloques a partir de entidades seleccionadas; puede usar `extensions` (adapter-specific templates) pero no puede crear/alterar entidades, refs, `state` ni relaciones. Entrada: vista de solo lectura del evidence + selección del Profile.
- **Renderer** (formato): `{renderer_id, format}` (md, json, …). Convierte un documento intermedio neutral (secciones/bloques) al formato. Sin lógica de selección ni de contenido.
- **Perfiles mínimos:** `human-functional` (audiencia funcional, ES por defecto, summary-first, flujos legibles, unresolved agrupado por causa), `human-technical` (audiencia técnica, apéndice de evidencia con refs), `ai-context` (consumidor IA; selección/empaquetado según D-08).
- **Default vs custom:** defaults empaquetados en `legacy_documenter/` (Runtime Independence); custom templates en directorio configurado por el usuario, mismo esquema y validación. Un template custom no puede sobrescribir defaults sin nombre distinto.
- **Versioning y cache key:** `projection_cache_key = SHA-256(evidence_snapshot | profile_id@version | template_id@version | renderer_id@version | language)`.
- **Validación:** esquema del template, compatibilidad Profile↔Template, existencia de secciones, y **verificación post-render**: el conjunto de IDs/refs citados ⊆ evidence y ninguna cifra contradice `summary_counts`.
- **Fallback:** si un template custom falla validación/render → `TEMPLATE_ERROR` estructurado; se usa el default del profile si `fallback=default` (por defecto) y se registra en `RUN_SUMMARY` (`warnings`); nunca se emite documentación parcial silenciosa. Si falla el default → el stage `DOCUMENTATION` = `FAILED` sin tocar evidencia.
- **Errores de template:** `TEMPLATE_NOT_FOUND`, `TEMPLATE_SCHEMA_INVALID`, `TEMPLATE_INCOMPATIBLE_PROFILE`, `TEMPLATE_RENDER_ERROR`, `TEMPLATE_TRUTH_VIOLATION` (contradice evidencia).
- **Invariante de verdad:** dos templates sobre la misma evidencia ⇒ mismos IDs citados válidos, refs, `state`, relaciones y `UnresolvedBoundary` (test: `template_truth_invariance`).

## PROVIDER CONTRACT

`LLMProvider` (ABC) pasa a exigir, además de `generate`, `capabilities`, `model_info`:
- `structured_generate(request, schema) -> LLMResponse` (obligatorio; en el ABC, con `UNSUPPORTED_CAPABILITY` si `structured_output=False`).
- `close()` / context manager: liberación idempotente de recursos; el orquestador siempre lo invoca en `finally` (incluye cliente SDK, sesiones, subprocesos).
- `capabilities()`: `context_window`, `max_output_tokens`, `structured_output`, `json_mode`, `system_instruction`, `temperature_control`, `streaming`, `tool_use` (declarados; el orquestador no asume lo no declarado).
- **Timeout/rate limit:** `timeout_s` en config; `RATE_LIMITED` con `retry_after` opcional; retry solo si el provider declara `retryable`; política de reintentos en el orquestador, no en el provider.
- **Estados:** `SUCCESS, CONTEXT_TOO_LARGE, INVALID_STRUCTURED_OUTPUT, PROVIDER_ERROR, TIMEOUT, RATE_LIMITED, UNSUPPORTED_CAPABILITY` (+ los ya existentes `INVALID_REQUEST`, `CANCELLED`, `PROVIDER_CONFIGURATION_ERROR` se mantienen por compatibilidad).
- **Presupuesto:** el gate de tamaño lo hace el orquestador sobre `measure_request_payload` (V4.3-R5), previo a cualquier llamada; el provider no reimplementa el gate.
- **Sanitización:** todo mensaje de error/persistencia pasa por el sanitizador central (hoy `_sanitize` en `copilot.py` — mover al núcleo en V5.5, compartido).
- **Credenciales:** solo por referencia (`credential_source`: nombre de variable/almacén), nunca valores en config persistida ni outputs.
- **Lazy SDK import:** el SDK del vendor se importa dentro de la llamada, nunca a nivel de módulo; su ausencia produce `PROVIDER_CONFIGURATION_ERROR`, no fallo de import.
- **Registro extensible:** `ProviderRegistry` deja de usar `if` por tipo; registra factories por `provider_type` (entrypoint interno o config), con `FAKE` siempre disponible. Selección/evidence no dependen del provider (V5.5 cambia providers sin tocar selection).
- **`GeminiProvider` → isolate:** hoy está sin registrar y no cumple el contrato (sin `close`, credencial por URL con `key=`); se marca no soportado y se excluye de la distribución hasta que V5.5 lo complete o retire.
- **Copilot:** un `asyncio.run` por llamada es aceptable pero debe garantizar `close()`; el `client.stop()` en `finally` ya existe.

## RUNTIME / TOOLING BOUNDARY

Clasificación (D-11):

| Módulo | Destino | Justificación |
|---|---|---|
| `knowledge/readiness.py` (+ `_readiness_*`) | **tooling de desarrollo** (+ subcomando `readiness` fuera de la distribución limpia) | lee `codex/V3/...` y `output/LEVANTAMIENTO_*` |
| `knowledge/closure/*` | **tooling de desarrollo** | lee `PROJECT_STATE.json` y `docs/V4/` |
| `documentation/human_review.py`, `second_review.py` | **legacy congelado** | escriben/leen `codex/V3`; `readiness` los importa (`EXTERNAL/PARTIAL/RESOLVED`) |
| `documentation/{generator,hierarchical,resume,systematic}`, `analysis/deep_*`, `llm/copilot_pilot.py` | **legacy congelado**, retiro en fase posterior | acoplados a Copilot vía `asyncio.run(discover_model())`; fuera del pipeline `full` |
| Resto de `knowledge/*` (canonical, approval, proposals, plugin_projection, provenance, …) | **runtime productivo** (su evolución en V5.7) | necesarios para proposals/approval |

**Frontera formal de la distribución limpia V5:** `main.py` + `legacy_documenter/` contiene solo runtime productivo; ningún módulo empaquetado lee `docs/`, `prompts/`, `tests/`, `PROJECT_STATE.json`, `governance/`, `codex/`, `output/` del repo de desarrollo. `router.py` no importa `readiness` a nivel de módulo (import diferido o subcomando de tooling). Verificación automatizable: (a) grep/AST de rutas prohibidas bajo el paquete runtime; (b) ejecutar `analyze/full/output-manifest` desde la distribución construida aislada, sin acceso a esas carpetas. La corrección de R9 ("ningún módulo lee docs/…") queda reclasificada: era cierta para el camino runtime, falsa para el paquete completo; V5 cierra esa brecha.

## OBSERVABILITY CONTRACT

Clave aditiva `observability` en `RUN_SUMMARY.json` (no toca `stages[]` existentes; lectores V4.3 ignoran claves desconocidas). Por stage (`observability.stages[stage_id]`):

| Métrica | Clase |
|---|---|
| `duration_ms` | **obligatoria** |
| `stage_started_at`, `stage_finished_at` (UTC ISO-8601) | **obligatoria** (fuera de la comparación byte-determinista: `RUN_SUMMARY` no participa en D-01) |
| `input_count`, `output_count` | **obligatoria** |
| `cache_hit`, `cache_miss` | opcional (presente desde V5.3; `null` antes) |
| `peak_memory_mb` | **diagnóstica** (best-effort, `null` si no medible en la plataforma) |
| `provider_calls`, `payload_estimated_tokens` (stages IA) | opcional |
| `threads_alive_at_exit` | diagnóstica (ver PROCESS EXIT) |

Nunca contienen paths con secretos ni contenido de fuente. Coste de medición debe ser despreciable (`perf_counter`); sin dependencias nuevas.

## INCREMENTAL / CACHE CONTRACT BOUNDARY

Solo contratos (algoritmos en V5.3):
- **File fingerprint:** SHA-256 del contenido + tamaño (ya en `SourceArtifact`).
- **Extractor version / adapter version / stage version / schema version:** siempre registrados en `EVIDENCE_MANIFEST.json`.
- **Reverse dependency index:** relación `SourceArtifact → {entidades producidas}` y `entidad → {flows que la contienen}` persistible como partición de evidencia (`evidence/reverse_index`); su schema se fija en V5.1, su uso en V5.3.
- **Invalidation unit:** por `SourceArtifact` en EXTRACTION; por `Project` para dependencias; por `FunctionalFlow` en resolución de flows (clausura transitiva); por partición en proyecciones.
- **Cache key (stage):** `SHA-256(stage_id@stage_version | adapter@version | fingerprints de entradas | parámetros relevantes, p. ej. flow_max_depth)`.
- **Projection cache key:** ver TEMPLATE. **Template version / Profile version:** parte de la clave.
- Garantía: añadir cache **no cambia IDs ni schema base** (D-05, D-14).

## SEGMENTATION FUTURE-PROOFING

`FunctionalFlow` (y `FunctionalPath` donde aplique) incluyen desde V5.1, como **opcionales con default neutro**:
`parent_flow_id` (null si no es segmento), `segment_id` (`SEG-`+SHA-256; null si flow completo), `partial` (bool, default false), `included_paths[]`, `omitted_paths[]` (IDs; vacío por defecto), `evidence_refs[]`, `segment_reason` (opcional).
Reglas: un segmento nunca redefine el flow padre (el flow completo sigue existiendo con `path_ids` íntegros); `included_paths ∪ omitted_paths = path_ids` del padre; un segmento `partial=true` debe listar `omitted_paths`; los IDs `FLOW-` V4.3 no cambian. V5.1 solo serializa estos campos con sus defaults; la lógica de segmentar es V5.6.

## APPROVAL / CANONICAL BOUNDARY

Pipeline conceptual con stores y entidades **separados**:
`Evidence` (`evidence/`) → `Proposal` (`proposals/`, `PRP-`; `evidence_refs` obligatorios, `status=PENDING_…`) → `HumanDecision` (nuevo, V5.7; `DEC-`; `proposal_id`, `decision`, `decided_by`, `rationale`, `decided_at`) → `CanonicalKnowledge` (nuevo, V5.7; `CAN-`; `derived_from_decision`, `evidence_refs`).
V5.1 debe: (a) no incluir en `evidence/` ningún dato de proposal/decisión/canónico; (b) garantizar que los `evidence_refs` de una proposal apunten a IDs de evidencia (no a texto); (c) no requerir cambios en evidencia para V5.7 (Approval solo **referencia** evidencia). Sin cambios: ninguna auto-aprobación ni canonicalización automática; `approval_surface_implementation` sigue `NOT_IMPLEMENTED` hasta V5.7.

## V4.3 → V5 MIGRATION STRATEGY

1. **V5.1:** introduce `evidence/` y el adapter de referencia envolviendo el código actual; `index/` se proyecta desde `evidence/` (D-04). Gate: D-01 sobre fixtures + IST.
2. **V5.2:** documentación por Profile/Template/Renderer con defaults equivalentes a V4.3; nuevas rutas aditivas.
3. **V5.3:** cache/incremental sobre `evidence/` (D-05, D-14).
4. **V5.4:** adapters adicionales/DB; el resolver de flows ya solo ve entidades neutrales.
5. **V5.5:** provider contract completo, registro extensible.
6. **V5.6–V5.8:** segmentación, approval/canonical, consumer/plugin.
7. **Transición:** durante V5.1–V5.3 conviven salidas V4.3 y `evidence/`; ningún consumidor V4.3 necesita cambios. `PROJECT_STATE.json`/baselines V4.3 no se editan retroactivamente; V5 abre su propia línea (ver TEST BASELINE RESOLUTION).
8. **Rollback:** cada fase es aditiva; desactivar `evidence/` deja el pipeline V4.3 intacto hasta V5.3.

## TEST BASELINE RESOLUTION

Clasificación de los 4 fallos (D-13):
- **Naturaleza:** *stale historical expectation* (tests obsoletos), no regresión de producción. Los tests V4-R13/R14 afirman `provider_calls==0`/`real_llm_calls==0` contra el `PROJECT_STATE.json` **vivo**, pero éste se avanza con cada ronda; V4.3 registró legítimamente 1 llamada real (piloto). El propio test hermano `test_baseline_matches_on_disk_artifact` ya documenta el patrón de campos que "avanzan legítimamente" (REG-002-CANDIDATE) y no lo aplicó a estos campos.
- **Fuente de verdad:** `PROJECT_STATE.json` **es la historia acumulada del proyecto**, no un baseline de fase; la información "0 llamadas reales durante V4" pertenece al artefacto congelado `output/v4_r14/V4_FINAL_BASELINE.json`.
- **Contradicción:** `PROJECT_STATE.json` (`test_failures: 0`) y R9 ("0 fallos") divergen de la ejecución real (4 fallos) → esos registros son **inexactos** desde el commit `44e2a94`; la suite V5 baseline **no** se declara verde.
- **Criterio de resolución para R2 (antes de autorizar V5.1):** R2 debe (1) reproducir los 4 fallos, (2) verificar que las 4 aserciones sean únicamente las de `provider_calls`/`real_llm_calls`/baseline-vs-live, (3) recomendar y solicitar aprobación del Líder Técnico para **una** de: reescribir esas aserciones a "monótono no decreciente respecto del snapshot congelado" (patrón REG-002) o mover la aserción de "0 llamadas" al artefacto congelado; (4) tras aprobación, aplicar el cambio de tests en una ronda separada, con `PROJECT_STATE.json` sin editar retroactivamente. Hasta entonces el baseline V5 = `2169 tests, 4 failures conocidas y clasificadas, 132 skips`.

## ACCEPTANCE CRITERIA FOR R2

R2 (validación, no implementación) debe demostrar, con evidencia:
1. **Round-trip viable:** sobre fixtures, las estructuras que hoy producen los resolvers pueden mapearse a las entidades del contrato sin pérdida de información (tabla campo→campo) y reproyectarse a `index/` (prototipo de solo lectura o análisis sobre índices reales existentes, sin modificar producción).
2. **IDs:** ejecutar el detector de colisiones sobre los índices IST existentes (`EP/FLOW/DAO/PATH`) y reportar 0 colisiones o el listado; decidir D-02 deferred con ese dato.
3. **Cobertura de campos:** todo campo de `index/*.json` V4.3 tiene destino en núcleo o `extensions`.
4. **Sin contaminación:** listado de campos WebForms/VB/Oracle en núcleo = vacío.
5. **Templates:** demostrar sobre entidades reales que la invariante `template_truth_invariance` es comprobable.
6. **Provider:** tabla de brechas ABC actual vs contrato; confirmar que `orchestration/ai_interpretation` solo usa métodos del contrato.
7. **Runtime independence:** análisis AST de referencias a rutas de desarrollo bajo el futuro paquete runtime; lista de módulos a mover/excluir (sin moverlos).
8. **Tests:** clasificación de los 4 fallos confirmada y propuesta aprobada (TEST BASELINE RESOLUTION).
9. **Cache/incremental:** confirmar que fingerprints/versiones/reverse index cabrían en el schema de V5.1 sin cambios posteriores.
10. **Observabilidad:** confirmar que `RUN_SUMMARY.json` acepta `observability` sin romper lectores V4.3 (test de lectura sobre `RUN_SUMMARY` existente).
11. **Tamaño:** estimación de tamaño/tiempo del store `evidence/` sobre IST (a partir de índices existentes) para confirmar el formato particionado.

Criterios de R1 (autoevaluación): (1) 9 decisiones abiertas → D-03, D-04, D-05, D-13, D-10, D-01, D-08, D-07/D-09, D-12 — cubiertas; (2) sin contradicciones internas (evidence canónica = `evidence/`, `index/` = proyección, D-01 en capas); (3) V5.2 solo consume `evidence/` — sí; (4) V5.3 usa campos ya previstos — sí; (5) V5.4 solo agrega adapters tras el contrato — sí; (6) V5.5 no toca selection/evidence — sí (D-08); (7) segmentación prevista — sí; (8) V5.7 solo referencia evidencia — sí; (9) frontera runtime explícita — sí; (10) tests clasificados con criterio — sí.

## RISKS

1. **Colisiones de ID `poly33`** no verificadas en IST (D-02); mitigación: detector en R2/V5.1.
2. **Byte-equivalencia de `index/`** puede fallar por orden de iteración/serialización al reprojectar; mitigación: gate D-01 desde el primer prototipo.
3. **Tamaño de `evidence/` + `index/` + `ai_context/`:** duplicación temporal (≈ +1 GB) hasta V5.3; mitigación: particionado y, opcionalmente, proyección `index/` bajo demanda (V5.3+).
4. **Contaminación residual de vocabulario** en `hydration`, `system_context_builder`, `pipeline_stages`; requiere adaptación cuidadosa sin cambiar salidas.
5. **`technical_documentation_renderer.py`** (1222 líneas) es difícil de reexpresar como template; riesgo de equivalencia semántica.
6. **Alcance:** V5.1 podría crecer si intenta reescribir resolvers; el contrato lo prohíbe (envolver, no reescribir).
7. **Provider:** asumir semántica común entre vendors (estructura JSON, timeouts); mitigar con capacidades declaradas.
8. **Tests V4 obsoletos** pueden normalizar "rojo aceptable"; R2 debe cerrar la clasificación antes de V5.1.
9. **Riesgo intermitente** `test_deterministic_run_then_ai_enabled_rerun_same_output` (V4.2-R6): sigue siendo trigger de investigación.
10. **Process exit** no observado en escala IST (NOT_REPRODUCED).

## DEFERRED ITEMS

- Formato físico de `evidence/` (JSONL vs JSON particionado) → V5.1 con medición.
- Algoritmos de invalidación/propagación → V5.3.
- Implementación de `close()` y registro extensible de providers, mover sanitizador → V5.5.
- Destino final de `GeminiProvider` (completar/retirar) → V5.5.
- Segmentación real → V5.6; Approval/Canonical → V5.7; contrato Plugin → V5.8.
- Retiro de módulos V3 legacy congelados → V5.9/V6.
- Corrección real de los 4 tests → ronda separada tras aprobación (R2).
- Esquema alterno de IDs (alias) solo si R2 detecta colisiones.

### PROCESS EXIT (estado: `NOT_REPRODUCED`)
Sin corrección especulativa. Si reaparece: capturar en el run afectado (a) `threading.enumerate()` y `multiprocessing.active_children()` al final de `FINAL_SUMMARY` (campo diagnóstico `threads_alive_at_exit`), (b) árbol de procesos hijos del PID (`psutil` no se agrega como dependencia; usar `tasklist`/`wmic` manual), (c) si el run tenía `--allow-ai-interpretation`, confirmar que se llamó `provider.close()`, (d) `faulthandler.dump_traceback_later(…)` opcional en modo diagnóstico, (e) reproducir con el mismo output/dataset. Sin nueva evidencia el estado no cambia.

## FILES READ

`AGENTS.md`, `PROJECT_STATE.json`, `prompts/V5_0/V5_0_R1_ARCHITECTURE_CONTRACT_REVISED_PROMPT.md`, `docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md`, `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`, `docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md` (parcial), `docs/V4_3/V4_3_R9_FINAL_CLOSURE_RESULT.md` (parcial, leído en R0), `legacy_documenter/analysis/{flow_resolver,database_resolver}.py` (derivación de IDs), `tests/test_v4_r13_regression_and_security.py` y `tests/test_v4_r14_manuals_and_final_baseline.py` (aserciones de `provider_calls`), `git log` de `PROJECT_STATE.json`.

## FILES MODIFIED

- Creado: `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md`.
- Creado: `docs/V5/V5_0_R2_CONTRACT_VALIDATION_PROPOSED_PROMPT.md` (prompt propuesto, no ejecutado).
- Ningún otro archivo modificado.
