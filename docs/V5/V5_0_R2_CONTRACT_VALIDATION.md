# V5.0 R2 — Contract Validation

## STATUS

`V5_0_R2_CONTRACT_CHANGES_REQUIRED`

Ronda de validación/documental. No se modificó producción, tests, CLI, providers, prompts ni `PROJECT_STATE.json`. No se ejecutó IA real ni un nuevo `full` IST. Las decisiones D-01…D-16 de R1 **no** se cambiaron: donde la evidencia las contradice se registra `CONTRACT_CONFLICT` y se propone un Decision Record (DR-R2-xx) para aprobación humana posterior. No se crea R3 (regla de la ronda: solo si `CONTRACTS_VALIDATED`).

Output real V4.3 usado (existente, solo lectura): `C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1` (índices 951 MB / 996 421 575 B). Comparación de estabilidad con `C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline`.

## EXECUTIVE SUMMARY

- Núcleo del contrato (evidence/ → proyección `index/`, templates, profile vs AI projection, cache, segmentación, approval) es **viable**, con restricciones no-breaking.
- **4 bloqueos** exigen Decision Records antes de R3/V5.1:
  1. **D-02 / identidades:** los IDs `EP-`, `FLOW-`, `DAO-`, `PATH-` tienen **0 colisiones** en IST (medido). Pero `PAR-` (5), `CALL-` (27) y `UNRES-` (25) **sí colisionan**, y R1 asigna "ID V4.3" a `Project`, `Component`, `ExternalDependency`, `Call`, `UnresolvedBoundary`: **ninguno de los cinco tiene un ID V4.3 persistido y estable**. → DR-R2-01.
  2. **Tabla de entidades incompleta** (criterio "todo campo V4.3 tiene destino"): sin destino en R1 → `nodes[]`/`edges[]` de flows, `instantiations`, `imports`, `EVB-`, `SP-`/`SQL-`/`PAR-`/`CONN-`, `configuration`, `repository`, aristas de `dependencies`/`functional_dependencies`, `solutions`, `logical_symbols`. Es completable de forma aditiva. → DR-R2-02.
  3. **D-12 observabilidad:** `RUN_SUMMARY.json` con `observability` + timestamps **rompe 3 tests vigentes** (byte-identidad entre runs, "sin timestamps", igualdad exacta de conjunto de campos). → DR-R2-03 (sidecar).
  4. **EvidenceReference:** la estructura de R1 es contradictoria (`{source_id, kind, locator}` "estructural" vs `entity_id/entity_kind` "obligatorios") y no cubre las 4 formas reales de referencia. → DR-R2-04.
- Los **4 tests rojos** se reprodujeron exactamente y se deben solo a `provider_calls`/`real_llm_calls` (PROJECT_STATE vivo 1/1 vs baseline congelado 0/0). Recomendación: **Opción A** (ver `RECOMMENDED_TEST_BASELINE_FIX`); requiere aprobación humana.
- Runtime Independence: separación viable; solo la cadena `router → readiness → human_review/second_review` referencia rutas de desarrollo dentro del cierre de imports de `main.py`.
- Formato físico recomendado del prototipo `evidence/`: **JSONL compacto particionado por tipo de entidad** (~0.67–0.88× del tamaño `index/` pretty-printed antes de deduplicar).

## D-01..D-16 VALIDATION MATRIX

| D | Estado | Evidencia / restricción |
|---|---|---|
| D-01 | VALIDATED_WITH_CONSTRAINTS | Ver "D-01 viability" abajo. `index/` es byte-estable entre dos runs IST reales (21/22 archivos idénticos; solo `repository.json` difiere por `duration_seconds`). Restricciones: orden de emisión, orden de claves, CRLF de plataforma, sanitizador. Resultado: `VIABLE_WITH_CONSTRAINTS`. |
| D-02 | **CONTRACT_CONFLICT** | 0 colisiones en EP/FLOW/DAO/PATH, pero colisiones reales en PAR/CALL/UNRES y 5 identidades asumidas inexistentes. DR-R2-01. |
| D-03 | VALIDATED_WITH_CONSTRAINTS | Persistencia particionada viable; formato recomendado JSONL (sección tamaño). Constraint: el store debe cubrir las entidades faltantes de DR-R2-02. |
| D-04 | VALIDATED_WITH_CONSTRAINTS | Round-trip `evidence/ → index/` viable solo tras completar la tabla de entidades (DR-R2-02) y conservar orden (`ordinal`/orden de línea). |
| D-05 | VALIDATED | Cache ≠ evidencia es consistente; no requiere campos en evidence. |
| D-06 | VALIDATED_WITH_CONSTRAINTS | V4.3 usa `confidence` con solo `{confirmed, unresolved}` (ningún `inferred` en IST real); `state` = renombre con proyección inversa a `confidence`. `promotion_basis` es campo nuevo sin dato V4.3 (vacío). Depende de DR-R2-04. |
| D-07 | VALIDATED_WITH_CONSTRAINTS | `template_truth_invariance` comprobable sobre 3 flows reales; la verificación post-render de refs `CALL-` requiere resolubilidad (DR-R2-01/04). |
| D-08 | VALIDATED | `select_flow_ids`, `AiProjectionBuilder.package`, `measure_request_payload` existen y consumen el dict legacy `ix` de `index/`; el Profile solo acota candidatos. |
| D-09 | VALIDATED_WITH_CONSTRAINTS | Reexpresión como default templates viable; equivalencia semántica aún sin oráculo definido; `technical_documentation_renderer.py` sigue siendo el riesgo. |
| D-10 | VALIDATED_WITH_CONSTRAINTS | Ver matriz de provider: brechas concretas, ninguna requiere tocar evidence/selection. |
| D-11 | VALIDATED_WITH_CONSTRAINTS | Separación viable; `readiness` es subcomando de CLI (parser `COMMANDS`), retirarlo de la distribución limpia es un cambio de CLI que debe declararse. |
| D-12 | **CONTRACT_CONFLICT** | Tests vigentes prohíben timestamps y claves adicionales en `RUN_SUMMARY.json`. DR-R2-03. |
| D-13 | VALIDATED | 4 fallos reproducidos y clasificados; recomendación única A. |
| D-14 | VALIDATED_WITH_CONSTRAINTS | Campos de cache caben sin breaking change; `files.json` V4.3 **no** tiene `sha256` → hash de archivo es trabajo nuevo de SCAN (coste I/O por medir en V5.3). |
| D-15 | VALIDATED_WITH_CONSTRAINTS | Suficientes; añadir invariantes `included ∩ omitted = ∅` e `included ⊆ padre`. `functional_flows.json` V4.3 no tiene `path_ids` (derivable de `functional_paths.flow_id`). |
| D-16 | VALIDATED | Stores separados sin campos de decisión/canónico en evidence; proposals ya referencian IDs de evidencia. |

## ROUND-TRIP FIELD MAPPING

Conteos reales IST. `EXT` = `extensions["vbnet-webforms-oracle"]`. `PROJ` = campo de proyección legacy (se reconstruye). `GAP` = sin destino en R1 (DR-R2-02). Regla general: `confidence` (V4.3) ⇄ `state` (V5).

| Índice V4.3 (n) | Campo V4.3 | Entidad / campo normalizado | EXT | Proyección legacy |
|---|---|---|---|---|
| files (15 151) | relative_path | SourceArtifact.path (posix) | ruta original con `\` (14 606 la usan) | `relative_path` con `\` |
| | extension, name, folder, file_type, size | SourceArtifact.{artifact_kind, size_bytes}; resto derivable de `path` | `file_type` vocabulario adapter | idem |
| | (sin `sha256` en V4.3) | SourceArtifact.sha256 = dato **nuevo** | — | no se proyecta |
| projects (259) | name, path, assembly_name, root_namespace, target_framework, output_type | Project.{name, root_path} | resto en EXT (.vbproj) | idem |
| | project_references, assembly_references | Project.dependencies[] → Project / ExternalDependency | include/GUID en EXT | idem |
| | compile_items, content_items, configurations | Project.artifact_refs[] | `configurations` en EXT | idem |
| solutions (113) | name, path, projects[] (type_guid, guid) | **GAP** (agrupación .sln; Project.member_of / SourceArtifact) | todo el `.sln` en EXT | idem |
| symbols (6 513) | name, kind, file, namespace*, accessibility, modifiers, inherits, implements | Component.{name, component_kind, source_ref} | namespaces, modifiers, inherits, implements | idem |
| | members[] | Component.members[] | — | idem |
| | namespace_confidence | Component.state | — | `namespace_confidence` |
| logical_symbols (1) | name, kind, partial, parts[], evidence, confidence | **GAP** (Component lógico/partial) | `partial`, `parts` | idem |
| webforms (3 346) | path, kind, directives, codebehind, codefile, inherits, master_page, registers, scripts, stylesheets, markup_events | Component (component_kind=`page`/`control`) + SourceArtifact | **todos** en EXT | idem |
| entry_points (12 662) | id, type, confidence, handler_method, evidence[], class_name, project | EntryPoint.{id, trigger_kind, state, handler_ref, provenance, component_id} | `webform`, `control`, `event` | idem |
| | outgoing_calls[] (8 481: expression, method_name, receiver, receiver_path, resolved_target, confidence, line) | **GAP**: llamadas anidadas en EP (¿Call con owner=EP?) | — | idem |
| event_bindings (12 662) | id `EVB-`, webform, control, control_type, event, handler, class_name, project, confidence, evidence | **GAP** (`EVB-` comparte dígitos con `EP-`; se reconstruye con prefijo) | todo en EXT | idem |
| calls (4 328 archivos; 230 356 calls; 40 278 inst.; 9 113 imports) | file + calls[] (expression, method_name, receiver, receiver_path, arguments_count, containing_*, evidence, resolved_target, resolved_project, confidence, candidates) | Call.{caller_ref, callee_ref \| callee_unresolved_target, state, evidence, arguments_summary} | receiver/receiver_path | agrupado por `file` |
| | instantiations[] (type_name, variable_name, containing_*, resolved_type) | **GAP** (no hay entidad `Instantiation`; origen de aristas `InstantiatesClass`) | — | idem |
| | imports[] (name, alias, kind) | **GAP** (VB `Imports`) | EXT en Component/SourceArtifact | idem |
| data_access (20 082) | id, operation_kind, class, method, project, confidence, evidence[], evidence_count, connection*, dynamic_sql | DataOperation.{id, operation_kind, target, state} | — | idem |
| | access_kind, provider, command_variable, command_type, command_text, stored_procedure, sql_operation | DataOperation.{store_kind, target} parcial | `provider`, `access_kind`, `command_*` | idem |
| data_parameters (74 633) | id `PAR-`, name, direction, db_type, data_type, size, source_expression, wrapper, command_variable, evidence | DataOperation.parameters[] (entidad propia por su `PAR-`) | direction/db_type/wrapper | idem |
| stored_procedures (5 389) | id `SP-`, name, package, procedure, evidence[] | **GAP**: objeto de almacén (nodo terminal de paths) | package/procedure | idem |
| sql_operations (3) | id `SQL-`, operation, command_text, dynamic_sql, evidence[] | **GAP** | — | idem |
| functional_paths (170 020) | path_id, flow_id, entry_point_id, nodes[], relation_types[], terminal_type, terminal_target, confidence, depth, evidence_refs[], project_sequence[] | FunctionalPath.{id, flow_id, entry_point_id, nodes, relation_types, terminal_type, terminal_target, state}; `evidence_refs`→provenance; `depth`, `project_sequence` derivables/EXT | — | idem |
| flow_unresolved (162 914) | mismos campos que paths; contenido idéntico a los paths con `terminal_type=unresolved_boundary` (verificado por `path_id`) pero **orden distinto** | UnresolvedBoundary (vista filtrada de FunctionalPath) | — | PROJ, requiere orden propio |
| functional_flows (12 642) | id, entry_point_id, confidence, status, has_confirmed_terminal, has_unresolved_boundary, depth, project_sequence, evidence[] | FunctionalFlow.{id, entry_point_id, state, summary_counts} | — | idem |
| | webform, event, handler, start_method | denormalización de EntryPoint | EXT | idem |
| | nodes[] (id, type, label, project), edges[] (source, target, type, confidence, evidence_refs), terminal_operations[] (IDs) | **GAP**: grafo del flow (no derivable solo de `paths`) | tipos WebForm/Handler/Event | idem |
| | (`path_ids` no existe en V4.3) | FunctionalFlow.path_ids[] = agrupar `paths` por `flow_id` | — | no se proyecta |
| flow_summary (dict) | 21 contadores | derivable de flows+paths (`_summary`) | — | PROJ (recalculada) |
| dependencies (26 961) | source, target, dependency_type, source_file, evidence (texto), confidence | **GAP** (aristas Solution→Project, referencias) → Project.dependencies / ExternalDependency | tipos | idem |
| functional_dependencies (335 698) | source, target, dependency_type, source_file, evidence, evidence_samples[], evidence_count, confidence | **GAP**: vista derivada de calls/instantiations/data ops | — | PROJ (derivable; orden a fijar) |
| configuration (60) | path, appSettings, connectionStrings, assemblies, authentication, … | **GAP** (config es dato de `SourceArtifact` + `ExternalDependency` de tipo almacén) | **todo** en EXT | idem |
| repository (dict) | root, stats, ignored[], duration_seconds | EVIDENCE_MANIFEST.source_snapshot + resumen de scan; `duration_seconds` fuera de evidence | `ignored`, `stats` | idem (excluir `duration_seconds` en D-01) |
| errors (0) | `[]` | errores estructurados (vacío) | — | idem |

**Conclusión §1:** **12 grupos de campos no tienen destino en la tabla de entidades de R1** (marcados GAP: solutions, logical_symbols, outgoing_calls, EVB, instantiations, imports, SP, SQL, grafo del flow, dependencies, functional_dependencies, configuration). Ningún dato es irrecuperable: todos caben como entidades adicionales o extensiones. El contrato R1 no puede afirmar hoy "ninguna información necesaria queda sin destino". → DR-R2-02.

## D-01 viability (`VIABLE_WITH_CONSTRAINTS`)

| Aspecto | Hallazgo empírico | Constraint |
|---|---|---|
| Serialización | `json.dumps(sanitize_data(data), indent=2, ensure_ascii=False)` vía `atomic_write_text` | La proyección debe usar exactamente esa llamada (incluido `sanitize_data`). |
| Fin de línea | `atomic_write_text` abre en modo texto: los archivos IST tienen CRLF (`\r\n`) en Windows | "Byte-idéntico" solo dentro de la misma plataforma/newline policy; el gate debe fijarla o normalizar. |
| Orden de claves | Orden de inserción del resolver (`id` primero); **no** `sort_keys` | Contradice la regla general R1 "claves ordenadas en persistencia canónica": el store canónico de evidence puede ordenar, pero el proyector debe reproducir el orden de claves de cada índice (plantilla fija por índice). |
| Orden de entidades | No es orden por ID ni por ruta: `entry_points`, `files`, `data_access`, `stored_procedures` no están ordenados por ninguna clave simple; `functional_flows`/`functional_paths` sí por `flow_id`; `flow_unresolved` tiene contenido igual al filtro de `paths` pero **otro orden** | R1 dice "ordering por id" para EntryPoint: falso en V4.3. El store debe **preservar el orden de emisión** (orden de líneas JSONL o `ordinal`) por partición y por índice derivado. |
| Nulls / omitidos | Los índices emiten `null` explícito (p. ej. `project: null`, `handler_method: null`) | La proyección debe distinguir `null` de ausencia; evidence no debe descartar nulls. |
| Listas vacías | Se emiten `[]` (p. ej. `implements: []`, `terminal_operations: []`) | Preservar. |
| Temporales | Solo `repository.json.duration_seconds` difiere entre dos runs IST reales (todos los demás SHA-256 idénticos) | La exclusión de D-01 (`duration_seconds`) queda **validada empíricamente** como suficiente. |
| Paths | Rutas con `\` (14 606/15 151 archivos); `SRC-` de R1 usa path posix | Guardar la ruta original o el transform inverso (biyectivo en Windows; validado: 15 151 únicas, también sin distinguir mayúsculas). |
| Conteos truncados | 3 registros de `data_access` con `evidence_count != len(evidence)` | Persistir `evidence_count` por separado; no recomputarlo. |

No se propone cambiar D-01.

## ID COLLISION RESULTS

Detector ejecutado sobre índices IST reales. "Colisión" = mismo ID con contenido distinto; para `CALL-`/`UNRES-` (no persistidos) se recomputó con la misma `_stable_id` (poly33 mod 1 000 000 007) y las mismas claves que `flow_resolver`.

| Kind | Fuente | entity_count | unique_id_count | collision_count | collision_examples |
|---|---|---|---|---|---|
| `EP-` | entry_points.json | 12 662 | 12 662 | **0** | — |
| `FLOW-` | functional_flows.json | 12 642 | 12 642 | **0** | — |
| `DAO-` | data_access.json | 20 082 | 20 082 | **0** | — |
| `PATH-` | functional_paths.json | 170 020 | 170 020 | **0** | (`flow_unresolved`: 162 914 únicos, todos ⊂ `functional_paths`) |
| `EVB-` | event_bindings.json | 12 662 | 12 662 | 0 | — |
| `SP-` | stored_procedures.json | 5 389 | 5 389 | 0 | — |
| `SQL-` | sql_operations.json | 3 | 3 | 0 | — |
| `PAR-` | data_parameters.json | 74 633 | 74 628 | **5** | `PAR-0479869637`: `VIND_COM_CNT` (sysContrato.modificar) vs `VIND_HAB_TAB` (blSUBAtencion.crearConSeq); `PAR-0564977625`, `PAR-0994527376`, `PAR-0498999190`, `PAR-0928048288` |
| `CALL-` (derivado) | calls.json | 230 356 registros / 228 973 tuplas distintas | 228 946 | **27** IDs con tuplas distintas | `CALL-0560707372`: (`ucADHImpCalResNoReb.ascx.vb`, 334, `Space(15)`) vs (`proyectos\slnADHTraspaso\…\ucADHMO716.ascx.vb`, 100, `BL.ParametrosGenerales.ParAlfNum.txLlenarDropDownList(…)`); `CALL-0416856342`; `CALL-0129898555`; `CALL-0332785460`; `CALL-0420344582` |
| `UNRES-` (derivado) | calls sin `resolved_target` | 216 172 IDs | — | **25** | derivado de `CALL-`+expresión |

Notas:
- Coincide con la estimación de cumpleaños de R1 (n²/2N): PAR 2.8 esperadas/5 observadas; CALL 26/27; UNRES 23/25; EP/FLOW/DAO ≈0.1–0.2/**0** observadas. El riesgo de R1 quedaba confirmado para los kinds con n>70 000.
- Además de las colisiones de hash, 1 383 registros de `calls` comparten la **misma tupla** (misma línea con llamadas idénticas): el ID `CALL-` no distingue instancias.
- Impacto en referencias: de 74 176 `CALL-` distintos citados en `evidence_refs` de paths, **18 son ambiguos** por colisión y **396** apuntan a varias instancias idénticas.
- Regla de la ronda aplicada: no se alteró ningún ID ni se inventaron alias. `EP/FLOW/DAO/PATH` limpios; `PAR/CALL/UNRES` → `CONTRACT_CHANGES_REQUIRED`.

## IDENTITY ASSUMPTION VALIDATION

| Identidad en R1 | ¿Existe ID V4.3? | ¿Estable/único? | ¿Entidad propia o embebida? | Veredicto |
|---|---|---|---|---|
| `Project` → "`PROJECT-…`" | **No**. `PROJECT-%03d` solo existe en `documentation/generator.py` (legacy congelado, posicional, no estable) | Clave natural `path` única (259/259; `name` no: 218; basename 216) | Entidad propia (`projects.json`) sin ID; los flows la referencian por `path` en `project_sequence` y nodos `Project` | **CONTRACT_CONFLICT** |
| `Component` → "ID V4.3 de símbolo/webform" | **No**: `symbols.json` y `webforms.json` no tienen `id` | `webforms.path` única (3 346); símbolos: (file,name,kind) 6 512/6 513 (1 duplicado: `cc\cc\ccTMP.vb`/`ccRma1`) | Entidad propia sin ID | **CONTRACT_CONFLICT** |
| `ExternalDependency` → "ID V4.3" | **No**: `dependencies.json` (26 961 aristas) sin `id`; `assembly_references` embebido en `projects` | — | Embebida / aristas | **CONTRACT_CONFLICT** |
| `Call` → "ID V4.3" | `CALL-` existe **solo transitoriamente** en `flow_resolver._call_ref`; no se persiste en `calls.json` (0 ids) | **No**: 27 colisiones + 1 383 duplicados de tupla | Embebida en `calls[]` de cada archivo | **CONTRACT_CONFLICT** |
| `UnresolvedBoundary` → "ID V4.3 en `flow_unresolved`" | `flow_unresolved` no tiene ID propio; solo `path_id`. `UNRES-` es un id de nodo derivado de la llamada | `UNRES-`: 25 colisiones; `path_id`: único (162 914) | Es una **vista filtrada** de `FunctionalPath` (contenido idéntico; orden distinto) | **CONTRACT_CONFLICT** |
| `EntryPoint` "inicia `FunctionalFlow` (1:1)" | `EP-` sí | único | — | **Inexacto**: 12 662 EP vs 12 642 flows; 20 EP `unresolved` con `handler_method=null` no tienen flow (1:0..1) |
| `FunctionalPath.nodes[]` | nodos método = texto `proyecto::clase.metodo` (minúsculas), sin ID; entidad **Method no existe** en R1 | ambiguo (sobrecargas colapsan) | — | Falta entidad `Method` / referencia de nodo (DR-R2-02) |

Ajuste mínimo propuesto: ver DR-R2-01.

## TECHNOLOGY NEUTRALITY

Resultado: **0 nombres de campo obligatorios** del core con semántica VB/WebForms/.NET/Oracle/ADO.NET/.vbproj en la tabla de entidades R1 (`Component`, `EntryPoint.trigger_kind`, `DataOperation.store_kind`, `Project` son neutrales). **Sí hay 3 vocabularios de valores** que filtran semántica tecnológica al core y deben declararse como enumeraciones abiertas namespaced por adapter:

| Campo core | Valores V4.3 con semántica tecnológica |
|---|---|
| `FunctionalPath.terminal_type` | `stored_procedure`, `sql` (semántica RDBMS/ADO); neutrales: `data_operation`, `unresolved_boundary`, `dead_end`, `cycle`, `truncated_depth` |
| `FunctionalPath.relation_types[]` | `Method -> UnresolvedCall`, `Method -> DataAccessOperation`, `DataAccessOperation -> StoredProcedure`, `DataAccessOperation -> SQL`, `Method -> InstantiatesClass` |
| `FunctionalPath.nodes[]` / `FunctionalFlow.nodes[].type` | tipos `WebForm`, `Handler`, `Event`, `Class`, `Project`, `DataAccessOperation`, `StoredProcedure`; etiquetas `proyecto::clase.metodo` en minúsculas (semántica VB case-insensitive) |

Campos V4.3 desnormalizados de alto riesgo (deben ir a EXT, no al core): `webform`, `control`, `event`, `directives`, `codebehind`, `provider`, `access_kind`, `command_variable`, `command_type`, `wrapper`, `direction`, `db_type`, `target_framework`, `root_namespace`, `type_guid`. Todos tienen sitio en `extensions[adapter_id]` sin cambiar el core. Estado: `VALIDATED_WITH_CONSTRAINTS` (constraint: vocabularios abiertos; la proyección legacy re-emite los valores V4.3 desde EXT/mapa).

## EVIDENCE REFERENCE VALIDATION

Referencias reales presentes en V4.3 (todas deben representarse):

| Forma real | Dónde | Cantidad / ejemplo |
|---|---|---|
| `CALL-` ID (no persistido) | `evidence_refs[]` de paths, `edges[].evidence_refs` | 214 204 refs en paths (74 176 distintas) |
| `DAO-` ID | `evidence_refs[]` de paths | 5 734; 0 sin resolver |
| Nodo `DAO-`/`SP-`/`SQL-`/`UNRES-` | `nodes[]` | 0 DAO / 0 SP sin resolver |
| Entidad como objeto | `functional_flows.evidence: [{"entry_point_id": …}]` | 12 642 flows |
| Ubicación de fuente + fragmento | `evidence[]` en EP/EVB/DAO/PAR/SP/SQL: `{file, line, expression, project, class_name, method}` | solo **línea** (sin columna); `expression` = **fragmento de fuente** |
| Texto técnico no-ID | `dependencies.evidence` (`"InitializeComponent()"`), `functional_dependencies.evidence/evidence_samples`, `symbols/logical_symbols.evidence` (`"Partial declarations"`) | 26 961 + 335 698 |
| Import con método nulo | `calls[].imports[].evidence` (`method: null`) | 9 113 |

Hallazgo: la fila `EvidenceReference` de R1 es **contradictoria** (identidad "estructural `{source_id, kind, locator}`" pero obligatorios `entity_id, entity_kind`), y `source_span (línea/columna)` promete columna que V4.3 nunca tuvo. **CONTRACT_CONFLICT** → DR-R2-04.

Subtipos explícitos necesarios (unión etiquetada, `ref_type`):
1. `entity` — `{entity_kind, entity_id}` (FLOW/PATH/EP/DAO/SP/…).
2. `source` — `{source_id: SRC-…, line?, excerpt?}` (cubre `file+line+expression`; `column`/`end_line` opcionales, `null` en V4.3).
3. `source_span` — opcional futuro (V5.4+), no requerido para V4.3.
4. `textual` — `{text, origin}` para referencias no-ID (dependencias, "Partial declarations").
Y un `legacy_ref` string para preservar `CALL-…` mientras coexistan IDs poly33 (resolución multi-candidato para los 18+396 ambiguos).
Soporta proposals/hydration/traceability/template appendix/consumer projection: hoy `package_reference_ids` y los `known_refs` de `ai_interpretation` operan solo sobre IDs de entidad → los subtipos 2–4 no afectan proposals (que exigen refs de entidad).

## TEMPLATE/PROFILE VALIDATION

Tres flows reales, conceptual, sin motor de templates ni IA:

| Flow | Estado real | Datos |
|---|---|---|
| trivial `FLOW-0002725421` | `dead_end`, `confirmed`, 1 path, 6 nodos, 3 aristas, sin terminal ops, 0 refs `CALL-` | proyecto `WebIndemnizacion.vbproj` |
| rico `FLOW-0000543312` | `unresolved_boundary`, `unresolved`, 149 paths (142 unresolved, 4 `data_operation`, 3 `stored_procedure`), 167 nodos/aristas, 7 DAO (7/7 resuelven; incluye `transaction`), 146 refs `CALL-`, 3 proyectos | terminal ops `DAO-0105548193`, … |
| unresolved `FLOW-0000051656` | `unresolved_boundary`, 2 paths, 8 nodos, 5 aristas, 2 `UNRES-`, 2 refs `CALL-` | `InitializeComponent()` |

Para cada uno los tres perfiles seleccionan sobre el **mismo** conjunto de entidades:
- `human-functional`: id + `state` + resumen (handler/evento → terminal) + unresolved agrupado por causa.
- `human-technical`: idem + todas las refs y apéndice de evidencia (paths, DAO, `CALL-`).
- `ai-context`: idem acotado por presupuesto (`select_flow_ids`/`package`).

Invariantes comprobadas (por diseño y sobre datos reales): (a) mismos IDs citados (`FLOW-`, `EP-`, `DAO-` resuelven 100 %); (b) `state` idéntico (rico y unresolved = `unresolved`; el trivial `confirmed`); (c) mismas relaciones (aristas/paths); (d) `UnresolvedBoundary` presente en los perfiles que incluyan `states ⊇ {unresolved}` y declarado en `omitted_*` cuando no; (e) diferencia solo de selección y redacción. `template_truth_invariance` es comprobable con el verificador post-render de R1 (IDs ⊆ store, cifras = `summary_counts`).
Punto débil: 396+18 refs `CALL-` ambiguas impiden "100 % refs resuelven" en el apéndice técnico hasta aplicar DR-R2-01/04. En estado real, el flow rico depende de esas refs (146).

Profile vs AI projection (D-08): `select_flow_ids(ix, max_flows)` y `AiProjectionBuilder.package(...)` consumen el dict legacy `ix` cargado de `index/` (`_run_evidence_io.load_indexes`); `measure_request_payload` opera sobre `LLMRequest`. Un Profile `ai-context` solo restringe qué entidades entran en `ix`; el algoritmo de budget/selección queda intacto. V5.2 **no** necesita mover budgeting al template engine, pero sí conservar la construcción de `ix` desde la proyección legacy. **VALIDATED.**

## PROVIDER CONTRACT GAP MATRIX

| Contract item | `LLMProvider` ABC actual | `FakeLLMProvider` | `CopilotProvider` | Orquestación actual | Gap |
|---|---|---|---|---|---|
| generate | abstracto | sí | sí (`asyncio.run` por llamada) | no lo usa | — |
| structured_generate | **no está en el ABC** (solo en implementaciones) | sí | sí | **la única llamada usada** (`ai_interpretation.py:181`) | subir al ABC; hoy el contrato depende de duck typing |
| capabilities | abstracto | desde `config.capabilities` | valores por defecto + config | lee `context_window`, `max_output_tokens` con `getattr` | ninguno |
| model_info | abstracto | sí | sí | no lo usa (usa `response.provider_id/model_id`) | — |
| close | **inexistente** | no aplica | limpieza interna en `finally` (`session.disconnect`, `client.stop`) | **nunca llama `close`** | añadir `close()`/context manager idempotente (V5.5) |
| timeout | no definido | no | `config.options["timeout"]` (60 por defecto; orquestador pasa 120); `TimeoutError`→`TIMEOUT` retryable | sin política de reintento propia | formalizar `timeout_s` |
| rate limit | — | — | **nadie produce `RATE_LIMITED`** (existe en `STATUSES`) | no maneja | gap real |
| retryability | `ProviderError.retryable` existe | — | `TIMEOUT` → true; otros false | **no reintenta**; reduce-and-retry solo de contexto | política de reintentos en orquestador (futuro) |
| structured output | `capabilities.structured_output` | valida `required` únicamente | valida `required` únicamente | valida con su propio validador (`FINDING_SCHEMA`, refs cerradas) | validación de schema es superficial en proveedores |
| json mode | `capabilities.json_mode` | declarado | declarado True | no lo usa | sin gap de contrato |
| context window | `capabilities.context_window` | compara con `context.statistics.estimated_tokens` (subestima) | no valida | **gate propio previo sobre `measure_request_payload`** | correcto: el gate está en el orquestador |
| max output | `capabilities.max_output_tokens` | sí | config | lo lee para el request | — |
| sanitization | — | — | `_sanitize` local (patrones de secretos) | `_sanitize_provider_error` propio | dos sanitizadores; consolidar en núcleo (V5.5) |
| credential_source | `ProviderConfig.credential_source` | — | **no se usa** (`use_logged_in_user=True`) | — | campo declarado sin consumidor en Copilot |
| lazy import | — | — | `from copilot import CopilotClient` dentro de `_generate` | — | cumple |
| registry | `ProviderRegistry.create` con `if` por tipo (`FAKE`, `COPILOT`) | disponible | disponible | `_resolve_provider()` construye `ProviderConfig` sin `context_window` | reemplazar `if` por factories registrables (V5.5) |
| Gemini | implementa el ABC sin `close`; credencial en URL (`?key=`) | — | no registrado | no usado | aislar (D-10 ya lo prevé) |
| `PROVIDER_CONFIGURATION_ERROR` | no es un status: es `error_code` (Gemini) | — | — | — | R1 lo lista como "status existente": inexacto; no hay cambio requerido |

**Confirmación:** `orchestration/ai_interpretation.py` usa solo `structured_generate` + `capabilities()` (`context_window`, `max_output_tokens`) + campos de `LLMResponse` (`status`, `provider_id`, `model_id`, `validation_errors`, `error`, `parsed_output`) + `measure_request_payload`. Todo cabe en el contrato R1. Ninguna brecha exige tocar evidence/selection. No se modificaron providers.

## RUNTIME INDEPENDENCE VALIDATION

Análisis AST (177 módulos: `main.py` + `legacy_documenter/`). Patrones: `PROJECT_STATE`, `docs/`, `prompts/`, `governance`, `codex/`, `tests/`, `output/LEVANTAMIENTO`, baselines V3/V4.

| Clase | Módulos | Detalle |
|---|---|---|
| Runtime productivo con referencias a rutas de desarrollo (en el cierre de imports de `main.py`, 87 módulos) | `knowledge.readiness` (+`_readiness_*`), `documentation.human_review`, `documentation.second_review` | Referencian `codex/V3/…` y `output/LEVANTAMIENTO_FUNCIONAL/TECNICO.md`. Son la única cadena: `cli.router` → `knowledge.readiness` → `human_review`/`second_review`. |
| Falsos positivos | `documentation.contracts`, `documentation.renderer` | Solo el título "LEVANTAMIENTO …" en plantillas de texto, no rutas. |
| Tooling de desarrollo (sin importadores; fuera del cierre de `main`) | `knowledge.closure.{baseline_report, manifest_report, artifact_hashes, maintainability}` | Leen `PROJECT_STATE.json`, `docs/V4/`, baselines. Nadie los importa: ya están desacoplados. |
| Legacy congelado (fuera del cierre) | `documentation.{generator, hierarchical, resume, systematic, consistency_run}`, `analysis.targeted_exhaustion`, `knowledge.classification.catalog`, `knowledge.projection.{contract_report, example_report, rules}`, `knowledge.domain.enums` | Referencias a rutas/nombres de desarrollo; no alcanzables desde `main`. |
| `analyze`, `full`, `output-manifest` | cierre de imports | Ninguna de las rutas `docs/`/`prompts/`/`tests/`/`PROJECT_STATE.json` aparece en el cierre salvo la cadena `readiness`. |

Viabilidad: sacar `readiness/closure/human_review/second_review` de la distribución limpia **no rompe** `analyze/full/output-manifest`: solo `router.py:20` importa `readiness` a nivel de módulo (`from …readiness import run as run_readiness`). Constraint: `readiness` es subcomando registrado (`COMMANDS` en `cli/parser.py`) con exit codes 0/1 cubiertos por tests; hacerlo import diferido conserva CLI y exit codes; retirarlo de la distribución limpia es un cambio de CLI que debe aprobarse. No se movió ningún archivo.

## OBSERVABILITY VALIDATION

`RUN_SUMMARY.json` real (V4.3, `full` + IA): 11 claves; `stages[]` con solo `{stage, status}`; sin ningún campo temporal.

Lectores reales:
- **Producción:** ninguno lee `RUN_SUMMARY.json`; solo se escribe (`run_summary_presenter.finalize_and_write_run_summary`) y `output_manifest.py` lo hashea como cualquier archivo.
- **Tests (lectores reales):**
  - `test_v4_3_r7_internal_acceptance.py:454` → `assertEqual(set(payload.keys()), expected_fields)` (11 claves exactas): **falla** si se añade `observability`.
  - `test_v4_2_r2_deterministic_full_pipeline_orchestrator.py:190-197` → `RUN_SUMMARY.json` idéntico entre dos runs equivalentes: **falla** si incluye `duration_ms` o timestamps.
  - Mismo módulo: `test_run_summary_json_has_no_uuid_or_timestamp_fields`: **falla** con `stage_started_at`/`stage_finished_at`.
  - `test_v4_2_r5…` (`PRE_R5_FIELDS.issubset`) tolera claves nuevas (aditivo OK).

Resultado: agregar `"observability": {}` vacío rompería solo el test de conjunto exacto; agregar `duration_ms`/timestamps rompe además determinismo y "sin timestamps". `input_count`/`output_count` (deterministas) podrían añadirse aditivamente pero también chocan con el test de conjunto exacto. **CONTRACT_CONFLICT (D-12).** → DR-R2-03.

## INCREMENTAL/CACHE FUTURE-PROOFING

Todos los elementos caben en el schema de V5.1 sin breaking change de evidence, con estas anotaciones:
- *file fingerprint*: V4.3 no tiene `sha256` (solo `size`); `SourceArtifact.sha256` es dato nuevo (lectura completa de 15 151 archivos en SCAN; coste a medir en V5.3).
- *adapter/extractor/stage/schema version*: campos nuevos de `EVIDENCE_MANIFEST` (no existen hoy).
- *reverse dependency index*: derivable (EP `evidence` → archivo; `paths` ↔ `flow_id`; `CALL-` ↔ archivo); requiere IDs de llamada sin ambigüedad (DR-R2-01).
- *flow invalidation*: unidad natural = `FunctionalFlow` (grafo por EP); el grafo `nodes/edges` debe estar en evidence (DR-R2-02).
- *projection cache key* y *template/profile version*: ya definidos en R1, no tocan evidence.
- Identidad y contenido: `SRC-`+SHA-256(path) ⇒ renombrar un archivo **crea un nuevo SourceArtifact** (y cambia `EP-`, que en V4.3 incluye la ruta del webform en su hash). Compatible con V5.3 si el *fingerprint* de contenido (sha256) se usa como clave de **reutilización de hechos** de extracción y no como identidad. No requiere cambiar la decisión.

## SEGMENTATION VALIDATION

Campos `parent_flow_id, segment_id, partial, included_paths, omitted_paths, evidence_refs, segment_reason` suficientes para V5.6 y no contaminan flows completos si son opcionales y **no se proyectan** en `functional_flows.json` legacy (verificado: el formato V4.3 no tiene ninguno; la proyección debe omitirlos para D-01).
Invariantes a explicitar (adición no-breaking): `included ∪ omitted = path_ids(padre)`, **`included ∩ omitted = ∅`** (necesaria; la unión sola admite solapamiento), `included ⊆ path_ids(padre)`, `partial=true ⇒ omitted ≠ ∅`, `partial=false ⇒ omitted = ∅`.
Nota: `path_ids` del flow no existe en V4.3 (se deriva de `paths.flow_id`); en el flow rico hay 149 paths (`170 020 / 12 642` = media 13.4), por lo que las segmentaciones reales operarán sobre listas de cientos de IDs.

## APPROVAL/CANONICAL VALIDATION

V5.1 puede mantener `evidence/`, `proposals/`, `decisions/`, `canonical/` separados. Estado actual: `proposals/` ya existe en V4.3 (`PENDING_TECHNICAL_LEAD_REVIEW`, `technical_lead_approval=false`, `canonical_knowledge_produced=false` en `RUN_SUMMARY.json`); ningún campo de decisión/canónico aparece en `index/`. `approval_surface_implementation=NOT_IMPLEMENTED`. Sin conflicto. Constraint: `evidence_refs` de proposals deben ser refs de tipo `entity` (DR-R2-04). **VALIDATED.**

## TEST BASELINE RESOLUTION

Reproducción (`python -m unittest tests.test_v4_r13_regression_and_security tests.test_v4_r14_manuals_and_final_baseline`): 92 tests, **4 fallos**, 0 errores.

| Test | Aserción | Causa |
|---|---|---|
| `test_v4_r13…:RepositoryContinuityStateTests.test_project_state_no_ai_or_provider_calls_recorded` (`:740`) | `PROJECT_STATE.provider_calls == 0` | vivo = 1 |
| `test_v4_r14…:EntryGateAndContinuityTests.test_project_state_readiness_ready` (`:89`) | `state["provider_calls"] == 0` | vivo = 1 |
| `test_v4_r14…:NoProviderOrLlmCallsTests.test_project_state_confirms_zero_calls` (`:510`) | `state["provider_calls"] == 0` | vivo = 1 |
| `test_v4_r14…:DeterminismTests.test_baseline_matches_on_disk_artifact` (`:334`) | baseline reconstruido == baseline en disco | diff **exactamente** `provider_calls 1≠0` y `real_llm_calls 1≠0` (verificado con `maxDiff=None`: solo esas 2 claves difieren) |

Se deben exclusivamente a `provider_calls`/`real_llm_calls` y a snapshot congelado vs `PROJECT_STATE` vivo. El artefacto congelado (`output/v4_r14/V4_FINAL_BASELINE.json`, commit `7c8e6ef`) mantiene 0/0 y su test (`test_provider_and_llm_calls_zero`, `:216`) **pasa**; `PROJECT_STATE.json` pasó a 1/1 en `44e2a94` (piloto real V4.3 autorizado).

`RECOMMENDED_TEST_BASELINE_FIX` — **Opción A**: mover las aserciones de "0 llamadas" al baseline congelado.
1. Los 3 tests que leen `PROJECT_STATE` vivo dejan de afirmar 0 llamadas (el hecho "V4 = 0 llamadas" ya está cubierto por `test_provider_and_llm_calls_zero` sobre el artefacto congelado).
2. `test_baseline_matches_on_disk_artifact` normaliza también `provider_calls` y `real_llm_calls` (mismo patrón REG-002 que ya usa para `test_count` etc.).
Razón frente a B: una aserción "monótona no decreciente" (`vivo ≥ congelado`) es casi vacía (1 ≥ 0) y no protege nada que el baseline congelado no proteja mejor; A conserva la invariante histórica en su lugar correcto y elimina la dependencia de `PROJECT_STATE`.
**Requiere aprobación humana del Líder Técnico antes de tocar tests. No se aplicó ningún cambio. No se declara la suite verde**: baseline V5 provisional = fallos conocidos 4 (clasificados); los conteos globales de R1 (2169 tests/132 skips) no se reejecutaron en esta ronda.

## EVIDENCE STORE SIZE/FORMAT ESTIMATE

Medición sobre índices reales (sin generar `evidence/`):

| Índice | pretty (actual) | compacto | JSONL.gz | registros | B/registro |
|---|---|---|---|---|---|
| entry_points | 30.3 MB | 21.7 MB | 1.6 MB | 12 662 | 1 712 |
| data_access | 26.6 MB | 20.5 MB | 1.2 MB | 20 082 | 1 018 |
| functional_paths | 124.2 MB | 97.5 MB | 12.8 MB | 170 020 | 573 |
| functional_flows | 124.2 MB | 86.3 MB | 8.7 MB | 12 642 | 6 824 |
| flow_unresolved | 118.3 MB | 92.8 MB | 11.2 MB | 162 914 | 569 |
| functional_dependencies | 227.2 MB | 200.5 MB | 8.5 MB | 335 698 | 597 |
| stored_procedures | 6.1 MB | 5.0 MB | 0.4 MB | 5 389 | 934 |
| symbols | 8.4 MB | 5.6 MB | 0.3 MB | 6 513 | 859 |

- `index/` total 996 MB; con `ai_context/` (279 MB), `consumer_projection/` (199 MB), `documentation/` (226 MB) el output completo ≈ 1.7 GB.
- Compacto/pretty ≈ 0.67–0.88 ⇒ `evidence/` completo ≈ **0.65–0.85 GB** sin deduplicar.
- Duplicación evitable: `flow_unresolved` (93 MB compacto) es contenido idéntico a un filtro de `functional_paths`; `functional_dependencies` (200 MB) y `dependencies` son vistas derivadas; `EVB` comparte contenido con `EP`; `flow_summary` es recomputable. Con ello `evidence/` bajaría a ≈ 0.35–0.5 GB.
- Coexistencia temporal `evidence/ + index/`: **+0.35–0.85 GB** (≈ +35–85 % sobre `index/`); menor que el "≈ +1 GB" estimado en R1.
- Lectura: `json.load` de 227 MB tarda 1.4 s en esta máquina; el JSON monolítico no es un problema de memoria/tiempo a escala IST, pero el archivo pretty de 227 MB sí lo es para diffs/particionado.
- Partición razonable: **~32–64 MB por partición** (≈ 50 000–100 000 registros pequeños; flows con 6.8 KB/registro ≈ 5 000–10 000 por partición).

`recommended physical format for V5.1 prototype`: **JSONL (UTF-8, LF) particionado por tipo de entidad, una entidad por línea, orden de emisión V4.3 preservado, más `EVIDENCE_MANIFEST.json` con SHA-256 por partición.** Justificación: (a) el orden de emisión es requisito de D-01 y JSONL lo hace intrínseco sin campo `ordinal`; (b) compacto ahorra ~25 %; (c) permite lectura por streaming y hash por partición para V5.3; (d) el proyector `index/` puede reescribir con el pretty-print exacto. JSON pretty particionado no aporta ventaja medida.

## CONTRACT CONFLICTS

| ID | Conflicto | Evidencia | Decision Record propuesto |
|---|---|---|---|
| CC-1 | `Project/Component/ExternalDependency/Call/UnresolvedBoundary` con "ID V4.3" inexistente o no único | ver "Identity Assumption Validation" | DR-R2-01 |
| CC-2 | `id_unique_per_kind` fallaría en IST (PAR 5, CALL 27, UNRES 25) | ver colisiones | DR-R2-01 |
| CC-3 | Tabla de entidades R1 sin destino para 12 grupos de campos | ver mapeo | DR-R2-02 |
| CC-4 | D-12: `observability`/timestamps incompatibles con 3 tests y con determinismo de `RUN_SUMMARY.json` | ver observabilidad | DR-R2-03 |
| CC-5 | `EvidenceReference` contradictoria / sin subtipos | ver EvidenceReference | DR-R2-04 |

### Decision Records propuestos (para aprobación; ninguno aplicado)

**DR-R2-01 — Alcance de D-02 y identidades no persistidas.** *Decision:* mantener D-02 (no re-derivar ni migrar IDs; el detector no renombra) pero (1) `id_unique_per_kind` se exige solo para los kinds cuyo ID es identidad de entidad: `EP, EVB, FLOW, DAO, SP, SQL, PATH` (0 colisiones medidas); (2) `PAR-`, `CALL-`, `UNRES-` pasan a **`legacy_ref`** no único (se preservan tal cual para `evidence_refs`/proyección legacy); (3) las entidades `Project, Component, ExternalDependency, Call, UnresolvedBoundary` reciben IDs **nuevos** V5 (D-02(b): SHA-256 completo, p. ej. `PRJ-`, `CMP-`, `XDP-`, `CAL-`) sobre su clave natural (`Project`: path; `Component`: (kind, file, name) + desempate ordinal; `Call`: tupla + ordinal de duplicado; `UnresolvedBoundary`: `path_id` del path terminal); (4) `EntryPoint`→`FunctionalFlow` pasa a 1:0..1. *Rationale:* IDs V4.3 poly33 no son identidad fiable para tipos de alta cardinalidad; los cinco tipos nunca tuvieron ID persistido.

**DR-R2-02 — Completar la tabla de entidades (aditivo).** Añadir a NORMALIZED EVIDENCE CONTRACT: `Method` (o referencia de nodo), `FlowGraph` en `FunctionalFlow` (`nodes[]`, `edges[]`, `terminal_operations[]`, `status`, `depth`, `project_sequence`), `DataObject` (SP/SQL con `SP-`/`SQL-`), `DataParameter` (`PAR-` como `legacy_ref`), `Instantiation`, `Import` (EXT), `EventBinding` (EXT de `EntryPoint`), `Solution`/agrupación, `ConfigurationEntry` (EXT de `SourceArtifact`), `ScanSummary`, e indicar que `flow_unresolved`, `flow_summary`, `functional_dependencies`, `dependencies` son **proyecciones** derivadas (con orden propio persistido). Sin cambiar ninguna D-xx.

**DR-R2-03 — D-12 vía sidecar.** *Decision:* mantener `RUN_SUMMARY.json` intacto (determinista, conjunto de campos exacto) y emitir métricas en un archivo aparte `RUN_OBSERVABILITY.json` (no participa en D-01; excluido de comparaciones deterministas); sus campos son los de R1. *Alternativa:* relajar 3 tests (requiere aprobación y ronda de tests). Se recomienda el sidecar.

**DR-R2-04 — EvidenceReference como unión etiquetada.** `ref_type ∈ {entity, source, source_span, textual}` (+ `legacy_ref` opcional) según la sección EvidenceReference; `promotion_basis` y `provenance` usan la unión; las proposals exigen `entity`.

## RISKS

1. Sin DR-R2-01/02, V5.1 heredaría colisiones y pérdida de información en el round-trip (D-04).
2. Orden de emisión no derivable de ninguna clave (incluso `flow_unresolved` difiere del filtro de `paths`): cualquier reordenación en el store rompe D-01.
3. Byte-identidad dependiente de CRLF/plataforma y del sanitizador.
4. `sha256` de archivos no existe en V4.3: coste de SCAN aún no medido.
5. 18 refs `CALL-` ambiguas + 396 multiinstancia afectan trazabilidad hasta resolver DR-R2-01/04.
6. Riesgo permanente: `technical_documentation_renderer.py` (D-09) y `readiness` como subcomando CLI (D-11).
7. Documentos R1 citan 2169 tests/132 skips y estados de `PROJECT_STATE` no re-verificados aquí.
8. Riesgo intermitente `test_deterministic_run_then_ai_enabled_rerun_same_output` (V4.2-R6) sigue como trigger de investigación; no se reprodujo en esta ronda (no se ejecutó la suite completa).

### Process Exit
`NOT_REPRODUCED` (sin nueva evidencia directa; sin investigación ni fix en esta ronda).

## TESTS / COMMANDS EXECUTED

- `python -m unittest tests.test_v4_r13_regression_and_security tests.test_v4_r14_manuals_and_final_baseline` → 92 tests, 4 fallos (los clasificados). Diff del baseline obtenido ejecutando `DeterminismTests.test_baseline_matches_on_disk_artifact` con `maxDiff=None` en un script inline.
- Scripts Python de solo lectura (fuera del repo, en el scratchpad de la sesión) sobre `…\v4_3_ai_rerun_r3a_r1_retry1\index\*.json`: inventario de claves, detector de colisiones (`EP/FLOW/DAO/PATH/EVB/SP/SQL/PAR` + recomputo `CALL/UNRES` con la `_stable_id` de `flow_resolver`), verificación de identidades, orden, resolubilidad de refs, comparación `OUTPUT_MANIFEST.json` entre dos runs IST, medición JSON/JSONL/gzip, análisis AST del grafo de imports (177 módulos).
- `grep` dirigido de `RUN_SUMMARY`, `provider.`, `CALL-`/`UNRES-`/`PROJECT-` en `legacy_documenter/` y `tests/`.
- No se ejecutó `full` IST, IA real, ni la suite completa.

## FILES READ

`AGENTS.md`, `CLAUDE.md` (vía contexto), `PROJECT_STATE.json`, `docs/V5/V5_0_R2_CONTRACT_VALIDATION_REVISED_PROMPT.md`, `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md`; índices `index/*.json`, `OUTPUT_MANIFEST.json` y `RUN_SUMMARY.json` de `v4_3_ai_rerun_r3a_r1_retry1` y `v4_3_rebaseline`; `legacy_documenter/{analysis/flow_resolver.py, analysis/database_resolver.py, exporters/json_exporter.py, utils/atomic_write.py, llm/core.py, llm/providers/{copilot,gemini}.py, orchestration/ai_interpretation.py, orchestration/_run_evidence_io.py, cli/{router,parser,output_manifest,run_summary_presenter}.py}` (parcial); `tests/test_v4_r13_regression_and_security.py`, `tests/test_v4_r14_manuals_and_final_baseline.py`, `tests/test_v4_2_r2_…`, `tests/test_v4_2_r5_…`, `tests/test_v4_3_r7_internal_acceptance.py` (parcial). Roadmap/lessons de `docs/continuity/` no se releyeron (ya citados por R1).

## FILES MODIFIED

- Creado: `docs/V5/V5_0_R2_CONTRACT_VALIDATION.md`.
- No se creó `V5_0_R3_FINAL_ARCHITECTURE_PACKAGE_PROPOSED_PROMPT.md` (R2 no quedó `CONTRACTS_VALIDATED`).
- Ningún otro archivo del repositorio modificado.
