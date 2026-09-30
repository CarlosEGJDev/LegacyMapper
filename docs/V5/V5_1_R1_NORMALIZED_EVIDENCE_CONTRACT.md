# V5.1 R1 — Normalized Evidence Core: Contract and Design

## STATUS

`V5_1_R1_CONTRACT_READY`

Ronda de diseño/documental. No se implementó V5.1, no se modificó producción, tests, `PROJECT_STATE.json`, providers ni el roadmap. No se ejecutó IA real. Ningún cambio se introdujo al contrato V5.0 ya aprobado (`docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`); este documento lo **aplica y detalla a nivel de implementación**, sin contradecirlo. Donde una decisión no tiene respaldo suficiente en V5.0 + R0 + código actual, se marca explícitamente `V5_1_R1_OPEN_DECISION` en línea, en vez de inventarse.

## LEE PRIMERO (confirmado)

`CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`, `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`, `docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md`, `docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md`, `docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md`.

Código actual inspeccionado para fundamentar cada decisión (no se asumió que el diseño de V5.0 ya estuviera implementado — no lo está): `legacy_documenter/models/{evidence,entry_point,call,project,source_file,symbol,webform,dependency}.py`, `legacy_documenter/analysis/{flow_resolver,database_resolver,web_entry_resolver,dependency_resolver,call_resolver}.py`, `legacy_documenter/extractors/{solution_extractor,webconfig_extractor,call_extractor}.py`, `legacy_documenter/utils/atomic_write.py`, `legacy_documenter/context/{consumer_projection,hydration}.py`, `legacy_documenter/cli/pipeline_stages.py`.

**Confirmación explícita:** ninguna de las clases `SourceArtifact`, `Solution`, `Component`, `Method`/`MethodReference`, `DataObject`, `Instantiation` (como entidad de primera clase), `ExternalDependency`, `FlowGraph` (como tipo propio), `UnresolvedBoundary` (como tipo propio) o `EvidenceReference` (como unión etiquetada) existe hoy en `legacy_documenter/models/`. Lo que existe son: `Evidence` (mapea 1:1 al subtipo `source` de `EvidenceReference`), `EntryPoint`/`EventBinding`, `Call`/`Instantiation`/`TypeReference` (import), `Project`, `SourceFile` (≈ `SourceArtifact` sin `sha256`), `Symbol` (≈ `Component`, sin ID propio), `WebForm` (parte de `Component`, hoy separado), `Dependency` (relación genérica no tipada, usada tanto para `Project -> ExternalDependency` como para docenas de otras relaciones). V5.1 diseña sobre esta base real, no sobre un modelo ya existente.

---

# 1. PRINCIPIO CENTRAL

```text
Legacy Source → Technology Adapter → Normalized Evidence Core → Evidence Persistence → Projections
```

Hoy (V4.3) esta cadena está **colapsada**: los extractores (`extractors/*`) producen dicts ya en vocabulario WebForms/VB/Oracle, los resolvers (`analysis/*`) los consumen directamente y el propio `index/*.json` es a la vez "evidencia" y "proyección legacy" en un solo paso, sin una capa normalizada intermedia. V5.1 introduce esa capa intermedia (`evidence/`) **envolviendo** el código actual (D-04/R1: "no reescribe resolvers"), no reemplazándolo. El *Technology Adapter* de referencia (`vbnet-webforms-oracle`) es, en esta ronda, una envoltura conceptual sobre los módulos ya listados en LEE PRIMERO — su implementación real es tarea de R2, no de R1.

V5.1 NO implementa (confirmado, sin cambios respecto a R3 §V5.1 OUT-OF-SCOPE): generic AI provider, nuevos providers, templates, profiles, incremental cache, segmentación avanzada, approval/canonical knowledge, plugin runtime, piloto multi-tecnología completo.

---

# 2 + 3. ENTIDADES MÍNIMAS Y CLASIFICACIÓN

Para cada entidad: Propósito · Identidad · Campos mínimos · Campos opcionales · Relaciones · Cardinalidad · Origen de datos · Clasificación · Preservación legacy · Evidencia primaria vs. derivado.

## SourceArtifact

- **Propósito:** representa un archivo físico del repositorio escaneado — la unidad atómica de la que toda evidencia deriva.
- **Identidad:** `SRC-`+SHA-256(path relativo POSIX). Nuevo (V5.0 D-02/D-03); no existe hoy.
- **Campos mínimos:** `path` (POSIX relativo), `sha256`, `size_bytes`, `artifact_kind`. `sha256` es dato **nuevo**: `SourceFile` (`legacy_documenter/models/source_file.py`) solo tiene `size`, nunca hash — respaldo: R0 §COMPARISON confirma que `files.json` V4.3 no tiene `sha256`; medirlo es I/O adicional de SCAN (ya señalado como riesgo en R3 §RISKS.6).
- **Campos opcionales:** `language`, `encoding`.
- **Relaciones:** pertenece a `Project` (vía `Project.artifact_refs[]`); es referenciado como `entity` desde `Component.source_ref` y como base de `EvidenceReference{ref_type: source}`.
- **Cardinalidad:** `1 Project : N SourceArtifact` (un artefacto pertenece típicamente a un proyecto; V0 nota que `files.json` no está particionado por proyecto hoy — la resolución `project_by_file` en `database_resolver._project_by_file` la reconstruye por `compile_items`).
- **Origen de datos:** `scanner/repository_scanner.py` + `scanner/file_classifier.py` (produce hoy `SourceFile`).
- **Clasificación:** `CORE_ENTITY`.
- **Preservación legacy:** `relative_path`/`extension`/`folder`/`name`/`file_type` de `SourceFile` se preservan íntegros (proyección legacy `files.json` los necesita byte a byte, D-01).
- **Evidencia primaria vs. derivado:** `path`/`size_bytes` primarios (medidos); `sha256` primario nuevo (medido, no derivado); `artifact_kind` derivable de `extension` (mapeo determinista, ya existe en `file_classifier.py`).

## Solution

- **Propósito:** agrupación `.sln` que enumera los `Project` que la componen.
- **Identidad:** `V5_1_R1_OPEN_DECISION` — R3 solo definió `Solution` como `core relation` (`Project.member_of`), sin ID propio. `SolutionExtractor.extract()` produce hoy `{name, path, projects[]}` sin `id`. No hay evidencia en R0 de que `Solution` necesite una identidad canónica más allá de su `path` (259 proyectos, 113 soluciones, R0 confirma 0 colisiones de identidad en el resto del árbol pero no midió `Solution` específicamente porque hoy no tiene ID). Se propone `SOL-`+SHA-256(path) por analogía directa con `Project`/`PRJ-`, pero se marca como decisión abierta hasta R2, que debe confirmar que ningún consumidor (proposals, hydration) necesita ya una forma distinta.
- **Campos mínimos:** `path`, `name`, `project_refs[]` (lista de `Project.id` una vez asignados).
- **Campos opcionales:** ninguno identificado con respaldo (el resto de `PROJECT_RE` — `type_guid`, `guid` — va a `extensions`, ver abajo).
- **Relaciones:** `Solution -> Project` (`core relation`, ya existe como `Dependency("Solution -> Project")` en `DependencyResolver._solution_deps`).
- **Cardinalidad:** `1 Solution : N Project`; un `Project` puede aparecer en más de una `Solution` (no verificado en R0; se asume N:M hasta que R2 mida lo contrario — `V5_1_R1_OPEN_DECISION`).
- **Origen de datos:** `extractors/solution_extractor.py` (regex sobre `.sln`).
- **Clasificación:** `CORE_RELATION` (agrupación mínima en el core, per R3 DR-R2-02) + `ADAPTER_EXTENSION` para `type_guid`/`guid` (específicos del formato `.sln` de Visual Studio, no neutrales a tecnología).
- **Preservación legacy:** `solutions.json` V4.3 (113 registros, R0) se reconstruye desde `Solution` + `extensions`.
- **Evidencia primaria:** el listado de proyectos referenciados es primario (leído del `.sln`); todo lo demás es igual.

## Project

- **Propósito:** unidad de compilación/despliegue (`.vbproj`).
- **Identidad:** `PRJ-`+SHA-256(path normalizado) (V5.0 D-02, R3 confirmado). Clave natural: `path`. R0 confirma 259/259 rutas únicas en el target real.
- **Campos mínimos:** `name`, `root_path` (= `path` de `Project` model actual), `artifact_refs[]` (deriva de `compile_items`+`content_items`).
- **Campos opcionales:** `kind` (deriva de `output_type`), `dependencies[]` (→ `Project`/`ExternalDependency`, hoy `project_references`/`assembly_references` en el modelo `Project` actual).
- **Relaciones:** `Project -> Component` (`core relation`, nueva — hoy implícita solo por `_project_by_file`/namespace matching, nunca materializada como arista de primera clase); `Project -> ExternalDependency`; `Project -> SourceArtifact` (`artifact_refs`); `Solution -> Project`.
- **Cardinalidad:** `1 Project : N Component`, `1 Project : N SourceArtifact`, `N Project : N ExternalDependency`.
- **Origen de datos:** `extractors/vbproj_extractor.py`.
- **Clasificación:** `CORE_ENTITY`.
- **Preservación legacy:** `assembly_name`, `root_namespace`, `target_framework`, `output_type`, `configurations` del modelo `Project` actual → `extensions["vbnet-webforms-oracle"]` (son específicos de `.vbproj`/.NET Framework, no neutrales — confirmado por R3 §TECHNOLOGY NEUTRALITY: `target_framework`/`root_namespace` están en la lista de "alto riesgo").
- **Evidencia primaria:** `name`, `path`, `compile_items`, `content_items`, referencias — todo leído directamente del XML del `.vbproj`, primario.

## Component

- **Propósito:** unidad de código con nombre (clase/módulo/interfaz/estructura VB.NET, o página/control WebForms) — fusión neutral de lo que hoy son `Symbol` y `WebForm` como conceptos separados.
- **Identidad:** `CMP-`+SHA-256(clave natural) (V5.0 D-02/DR-R2-01, R3). Clave natural: `component_kind + source_ref + name` + discriminador determinista. **Riesgo confirmado por R0:** existe 1 colisión real de `(file, name, kind)` en el target medido (`cc\cc\ccTMP.vb`/`ccRma1` según R2; R0 no repitió esta medición específica de duplicados de símbolo, solo la de IDs persistidos — queda como `V5_1_R1_OPEN_DECISION` el discriminador exacto: R2 propuso "ordinal determinista", pero el código actual (`Symbol` en `legacy_documenter/models/symbol.py`) no tiene ningún campo que sirva de ordinal natural entre dos símbolos con la misma tupla `(file, name, kind)`; R2 de V5.1 debe definir uno (p. ej. orden de aparición dentro del archivo) y verificarlo contra el caso real conocido.
- **Campos mínimos:** `name`, `component_kind` (valor abierto: `class`/`interface`/`module`/`structure`/`page`/`control`, namespaced si es necesario), `project_id`, `source_ref` (→ `SourceArtifact`).
- **Campos opcionales:** `parent_id` (para el caso `logical_symbols`: `partial=True`, `parts[]` → otros `Component`), `members[]`.
- **Relaciones:** `Project -> Component`; `Component -> Method` (`core relation`, nueva); `Component -> EntryPoint` (para `component_kind` WebForms/control); `Component -> Call` (emite llamadas).
- **Cardinalidad:** `1 Project : N Component`; `1 Component : N Method`.
- **Origen de datos:** `extractors/vbnet_extractor.py` (produce `Symbol`) + `extractors/webforms_extractor.py` (produce `WebForm`). Estos dos extractores hoy son **independientes** — no hay unificación en código; el Adapter de R2 debe fusionarlos en una sola entidad `Component`, sin cambiar su lógica de extracción (D-04).
- **Clasificación:** `CORE_ENTITY` para `name`/`component_kind`/`source_ref`/`parent_id`/`members`; `ADAPTER_EXTENSION` para `namespace`/`modifiers`/`inherits`/`implements`/`accessibility` (VB.NET) y `directives`/`codebehind`/`codefile`/`master_page`/`registers`/`scripts`/`stylesheets`/`markup_events` (WebForms) — ambos grupos son vocabularios de tecnología, confirmados como "alto riesgo" por R3 §TECHNOLOGY NEUTRALITY.
- **Preservación legacy:** `namespace_confidence` (→ `Component.state`, mapeo directo `confidence`⇄`state` de D-06); `webforms.json`/`symbols.json` V4.3 se reconstruyen por proyección desde `Component`+`extensions`.
- **Evidencia primaria:** nombre, tipo, archivo fuente — todo primario, extraído por regex/parsing determinista del código fuente (`vbnet_extractor.py`, `webforms_extractor.py`).

## Method / MethodReference

- **Propósito:** unidad ejecutable dentro de un `Component`; `MethodReference` es la forma en que `FunctionalPath.nodes[]` cita un método sin ID propio hoy.
- **Identidad:** `V5_1_R1_OPEN_DECISION`. R3 lo introdujo como "referencia de nodo", no como entidad con ID persistido propio. Hoy (`flow_resolver._method_label`/`_method_key`) un método se identifica por la tupla `(project, class, method)` formateada como texto `proyecto::clase.metodo` en minúsculas (`_flow_key_labels.py`) — **sin ID**, sin distinguir sobrecargas (confirmado defecto conocido de R2: "nodos método... ambiguo: sobrecargas colapsan"). R2 de V5.1 debe decidir si `Method` recibe un ID V5 nuevo (`MTH-`+SHA-256 sobre `component_id + method_name + signature` si hay señal de sobrecarga) o si permanece como referencia estructural sin entidad propia (`MethodReference` sería entonces solo un subtipo de `EvidenceReference`, no una entidad). Esta ronda no decide esto por sí misma porque el código actual no distingue sobrecargas y no hay evidencia de R0 sobre cuántas colisiones de `(class, method)` existen en el target real — inventar un ID sin esa medición violaría la regla "no inventar campos".
- **Campos mínimos (si se decide entidad):** `component_id`, `name`.
- **Relaciones:** `Component -> Method`; `Method -> MethodReference` (`Method` es la entidad; `MethodReference` es su cita en un nodo de `FunctionalPath`).
- **Clasificación:** `CORE_ENTITY` si R2 confirma que necesita identidad propia; en caso contrario, `Method` colapsa en `Component.members[]` + `MethodReference` como forma de `EvidenceReference{ref_type: entity, entity_kind: Component}` con un campo textual adicional para el nombre del método — ambas alternativas son válidas y se dejan abiertas.
- **Origen de datos:** `_flow_key_labels.method_key`/`method_label` (actual, sin ID).

## EntryPoint

- **Propósito:** punto donde el pipeline de handlers de eventos WebForms comienza un flujo funcional.
- **Identidad:** `EP-` preservado (V5.0 D-02, R0 confirma 0 colisiones/12 662). Producido hoy por `web_entry_resolver._add_binding_and_entry` vía `_stable_id("EP", form_path, control, event, handler_name)`.
- **Campos mínimos:** `component_id` (nuevo — hoy `class_name`/`project`/`webform` sueltos, sin referencia tipada a `Component`), `trigger_kind` (= `type` actual: `web_lifecycle`/`web_event`, ya neutral), `handler_ref` (→ `Method`, hoy `handler_method` como texto `Clase.Metodo`), `state` (= `confidence` actual).
- **Campos opcionales:** `trigger_label` (= `event`/`control` actuales, namespaced en la práctica pues son términos WebForms — ver clasificación).
- **Relaciones:** `EntryPoint -> FunctionalFlow` (**`1 : 0..1`**, no `1:1` — corregido por V5.0 D-02/R3, confirmado en R0: 12 662 EntryPoints vs 12 642 flows en el target real, 20 EntryPoints sin flow); `EntryPoint -> EventBinding` (comparten la misma tupla `(webform, control, event, handler)` pero son entidades separadas, D-02/DR-R2-02 — nunca fusionar `EVB-` dentro de `EP-`); `Component -> EntryPoint`.
- **Cardinalidad:** confirmada arriba.
- **Origen de datos:** `analysis/web_entry_resolver.py`.
- **Clasificación:** `CORE_ENTITY` para `component_id`/`trigger_kind`/`handler_ref`/`state`; `ADAPTER_EXTENSION` para el valor concreto `webform`/`control`/`event` en tanto vocabulario WebForms (el *campo* `trigger_kind`/`trigger_label` es neutral; su *valor* (`"web_event"`, control ASP.NET) es específico de tecnología — mismo patrón que R3 §TECHNOLOGY NEUTRALITY documenta para vocabularios abiertos).
- **Preservación legacy:** `outgoing_calls[]` (8 481 registros en R2/R0) → `CORE_RELATION` `Call.owner_entry_point_id` (DR-R2-02), no un campo embebido en `EntryPoint`.
- **Evidencia primaria:** `handler_method`/`confidence` son resultado de una resolución determinista (match de nombre de handler contra métodos del `Component`), no evidencia cruda — es evidencia primaria **derivada por un resolver determinista con criterio citado** (coincide con D-06: solo un resolver determinista puede promover `unresolved → confirmed`, y aquí lo hace con `handlers_by_name` como base).

## EventBinding

- **Propósito:** registro de que un control WebForms está enlazado a un método manejador — entidad hermana de `EntryPoint`, comparte la misma tupla de origen pero es semánticamente distinta (un binding de evento vs. el punto de entrada de ejecución que ese binding activa).
- **Identidad:** `EVB-` preservado (R0: 0 colisiones/12 662).
- **Campos mínimos:** `component_id`, `control`, `event`, `handler_ref`, `state`.
- **Relaciones:** `EntryPoint -> EventBinding` (misma tupla origen, entidades separadas, D-02/DR-R2-02); `Component -> EventBinding`.
- **Origen de datos:** `analysis/web_entry_resolver.py` (`EventBinding` model actual).
- **Clasificación:** `CORE_ENTITY` (campos), `ADAPTER_EXTENSION` (`control_type` es vocabulario ASP.NET).
- **Preservación legacy:** total — `event_bindings.json` V4.3 se reconstruye 1:1.

## Call

- **Propósito:** invocación de un método desde otro, resuelta o no.
- **Identidad:** `CAL-`+SHA-256(clave natural) (V5.0 D-02/DR-R2-01, R3). Clave natural: `source_artifact + containing_symbol + line + expression + duplicate_ordinal`. R0 confirma sobre el target real: 230 356 registros, 228 946 IDs poly33 únicos (formula legacy), 27 colisiones, y **880 grupos de tupla idéntica con 2 263 registros totales (1 383 "extra")** — el `duplicate_ordinal` es indispensable, no opcional: sin él, `CAL-` no sería identidad única ni siquiera con SHA-256 completo, porque dos `Call` con exactamente la misma tupla `(file, line, expression, resolved_target)` son legítimamente dos entidades distintas (dos invocaciones textualmente idénticas en el código). El ordinal debe derivarse de la posición determinista del registro dentro de la lista `calls[]` de su `SourceArtifact` (el orden de emisión del extractor ya es determinista, confirmado por R0/R2 — D-01 exige preservar ese orden de todos modos).
- **Campos mínimos:** `caller_ref` (→ `Method`/`MethodReference`, hoy `containing_class`+`containing_method`), `callee_ref` (→ `Method`) **o** `callee_unresolved_target` (texto, cuando no resuelve), `state` (= `confidence`), `evidence` (→ `EvidenceReference{ref_type: source}`).
- **Campos opcionales:** `arguments_summary` (= `arguments_count`/`candidates` actuales), `owner_entry_point_id` (cubre `outgoing_calls[]`, DR-R2-02).
- **Relaciones:** `Component -> Call` (emite), `FunctionalPath -> Call` (evidence_refs), `Call -> UnresolvedBoundary` (cuando `state=unresolved`).
- **Cardinalidad:** `1 Component : N Call`.
- **Origen de datos:** `extractors/call_extractor.py` (produce `Call` crudo con `receiver`/`receiver_path`/`resolved_target`) + `analysis/call_resolver.py` (resuelve `resolved_target`).
- **Clasificación:** `CORE_ENTITY` para los campos de arriba; `ADAPTER_EXTENSION` para `receiver`/`receiver_path` (sintaxis VB.NET de acceso a miembro).
- **Preservación legacy:** el `CALL-` poly33 transitorio de `flow_resolver._call_ref` (nunca persistido en `calls.json` hoy — confirmado por R0/R2) se preserva como `legacy_ref` opcional, no como `id`.
- **Evidencia primaria:** `expression`/`method_name`/`receiver`/línea son primarios (leídos del código fuente); `resolved_target`/`confidence` son derivados por `call_resolver.py` con criterio determinista citado (D-06).

## Instantiation

- **Propósito:** creación de una instancia de tipo (`New X(...)`/`Dim x As New X`).
- **Identidad:** sin identidad canónica propia (no está en la lista de prefijos V5.0); se referencia por posición dentro de su `SourceArtifact`, igual que `Call` sin duplicate_ordinal explícito salvo que R2 demuestre que hace falta (no medido en R0: `instantiations` no se contó específicamente para colisiones porque nunca tuvo ID en V4.3; R2 de V5.1 hereda esta laguna de medición — `V5_1_R1_OPEN_DECISION` menor, de bajo riesgo porque no es una identidad requerida por ningún consumidor conocido).
- **Campos mínimos:** `type_name`, `variable_name` (opcional), `containing_symbol_ref` (→ `Method`/`Component`), `evidence`.
- **Campos opcionales:** `resolved_type_ref`, `state` (= `confidence`, hoy `"unresolved"` por defecto en el modelo `Instantiation` actual).
- **Relaciones:** origen de la relación `Method -> InstantiatesClass` (ya existe como `relation_type` en `FunctionalPath.relation_types[]`, ver R3 §TECHNOLOGY NEUTRALITY).
- **Origen de datos:** `extractors/call_extractor.py` (mismo extractor que `Call`, produce `Instantiation` ya como dataclass propia — confirmado en código, R3/DR-R2-02 lo daba como GAP porque no tenía representación en `index/*.json` como entidad top-level, pero **sí existe como dataclass en el modelo actual**, simplemente sin exportarse como índice propio; corrección menor respecto a la caracterización de R2/R3, sin contradecir su clasificación final: sigue siendo `CORE_ENTITY` nueva a nivel de `evidence/`, aunque el código de extracción ya la produce).
- **Clasificación:** `CORE_ENTITY`.

## DataOperation

- **Propósito:** una operación de acceso a datos (lectura/escritura/transacción) contra un almacén.
- **Identidad:** `DAO-` preservado (R0: 0 colisiones/20 082).
- **Campos mínimos:** `operation_kind`, `store_kind` (nuevo nombre neutral — hoy `provider`/`access_kind` mezclan proveedor ADO.NET y tipo de operación), `target` (nombre de tabla/SP/consulta o `"unknown"`), `state`.
- **Campos opcionales:** `parameters[]` (→ `DataParameter`), `transaction_verb` (para `operation_kind="transaction"`, ver `database_resolver`: `"Method -> TransactionOperation"` vs `"Method -> DataAccessOperation"`).
- **Relaciones:** `Component/Method -> DataOperation` (vía `_method_id`, texto `proyecto::clase.metodo`, mismo problema de referencia de nodo sin ID que `Method` arriba); `DataOperation -> DataObject` (SP/SQL terminal); `DataOperation -> DataParameter`; `DataOperation -> ExternalDependency` (conexión, hoy `CONN-` en `database_resolver` — **GAP no cubierto por R3**: el `_stable_id("CONN", ...)` genera una arista `DataAccessOperation -> Connection` en `dependencies.json`, pero `Connection`/`CONN-` nunca se mencionó en R1/R2/R3 como identidad V5 ni como entidad — se marca `V5_1_R1_OPEN_DECISION`: probablemente deba modelarse como `ExternalDependency` de tipo store, consistente con R3 §NORMALIZED EVIDENCE CONTRACT ("`ExternalDependency` referenciada por `Project`"), pero eso nunca se verificó explícitamente contra este hallazgo de código; R2 debe decidirlo con evidencia).
- **Cardinalidad:** `target=unknown ⇒ state=unresolved` (invariante ya en R3).
- **Origen de datos:** `extractors/database_extractor.py` + `analysis/database_resolver.py`.
- **Clasificación:** `CORE_ENTITY` para campos neutrales; `ADAPTER_EXTENSION` para `provider`/`access_kind`/`command_variable`/`command_type`/`wrapper` (Oracle/ADO.NET).
- **Evidencia primaria:** operación cruda leída del código (`command_variable`, `stored_procedure`); `state` derivado por el resolver con criterio citado.

## DataObject

- **Propósito:** objeto de almacén terminal de un `FunctionalPath` — stored procedure o sentencia SQL.
- **Identidad:** `SP-` preservado (R0: 0/5 389) y `SQL-` preservado (R0: 0/3).
- **Campos mínimos:** `object_kind` (`stored_procedure`|`sql`), `name`/`command_text`, `state`.
- **Campos opcionales:** `package`/`procedure` (descomposición de `SP-`), `dynamic_sql` (para `SQL-`).
- **Relaciones:** `DataOperation -> DataObject`; `FunctionalPath -> DataObject` (terminal).
- **Origen de datos:** `analysis/database_resolver.py` (`stored_procedures`/`sql_operations` dicts).
- **Clasificación:** `CORE_ENTITY`.

## DataParameter

- **Propósito:** parámetro de una `DataOperation`.
- **Identidad:** **ninguna canónica** — `PAR-` es `legacy_ref` únicamente (V5.0 DR-R2-01, R0 confirma 5 colisiones reales/74 633). Identidad estructural: hijo posicional de `DataOperation.parameters[]`, sin ID propio en V5.
- **Campos mínimos:** `name`, `direction`, `state`.
- **Campos opcionales:** `db_type`, `data_type`, `size`, `source_expression`, `legacy_ref` (=`PAR-` original).
- **Relaciones:** `DataOperation -> DataParameter` (composición, no referencia — un `DataParameter` no existe fuera de su `DataOperation`).
- **Origen de datos:** `analysis/database_resolver.py` (`data_parameters` dict, clave `(project, class, method, command_variable, name, source_expression)`).
- **Clasificación:** `CORE_ENTITY` (existe en todo target VB/Oracle real) con `ADAPTER_EXTENSION` para `wrapper`/`db_type` (vocabulario ADO.NET).

## ExternalDependency

- **Propósito:** dependencia externa de un `Project` (ensamblado/DLL, conexión de datos, u otro recurso no perteneciente al repositorio analizado).
- **Identidad:** `XDP-`+SHA-256(clave natural) (V5.0 D-02, R3). Clave natural: `dependency_kind + source + target + metadata mínima estable`. **Sin medición de colisión en R0** (no existía como entidad con ID en V4.3, por lo que R0 no pudo ejecutar el detector sobre ella — mismo patrón que `Solution`; `V5_1_R1_OPEN_DECISION` menor: R2 debe ejecutar el detector una vez la entidad exista realmente).
- **Campos mínimos:** `name`, `dependency_kind` (abierto: `assembly`|`project`|`connection`|…).
- **Campos opcionales:** `version`, `source_ref`.
- **Relaciones:** `Project -> ExternalDependency`; potencialmente `DataOperation -> ExternalDependency` (ver `V5_1_R1_OPEN_DECISION` de `CONN-` arriba).
- **Origen de datos:** hoy embebida como aristas `Dependency("Project -> DLL", ...)` en `dependency_resolver._project_deps`, nunca materializada como entidad propia — confirmado, coincide exactamente con el `CONTRACT_CONFLICT` CC-1 que R2/R3 ya documentaron.
- **Clasificación:** `CORE_ENTITY`.

## FunctionalPath

- **Propósito:** un camino de ejecución concreto desde un `EntryPoint`, con su secuencia de nodos y su terminal.
- **Identidad:** `PATH-`+SHA-256 preservado (V5.0 D-02, R0: 0 colisiones/170 020). Fórmula exacta confirmada en código (`flow_resolver._path_id`): SHA-256 sobre JSON canónico de `{entry_point_id, nodes, relation_types, terminal_type, terminal_target}` — **no incluye `confidence`/`depth`/`evidence_refs`**, por lo que dos ejecuciones del resolver que produzcan la misma secuencia lógica siempre coinciden en ID, exactamente lo que D-01 necesita para estabilidad entre runs.
- **Campos mínimos:** `entry_point_id`, `nodes[]` (hoy texto, ver `Method`/`MethodReference` open decision), `relation_types[]`, `terminal_type`, `terminal_target`, `state` (=`confidence`).
- **Campos opcionales:** `depth` (derivable: `len(nodes)-1`, confirmado en código), `project_sequence` (derivable de `nodes`, confirmado: `_project_sequence_from_nodes`).
- **Relaciones:** `FunctionalFlow -> FunctionalPath`; `FunctionalPath -> Call` (vía `evidence_refs`); `FunctionalPath -> DataOperation`/`DataObject` (terminal); `FunctionalPath -> UnresolvedBoundary` (cuando `terminal_type` ∈ {`unresolved_boundary`,`cycle`,`truncated_depth`}).
- **Cardinalidad:** `1 FunctionalFlow : N FunctionalPath`.
- **Origen de datos:** `analysis/flow_resolver.py::_add_path`/`_walk`.
- **Clasificación:** `CORE_ENTITY`. `terminal_type ∈ {stored_procedure, sql}` es vocabulario RDBMS (R3 §TECHNOLOGY NEUTRALITY); los valores neutrales (`data_operation`, `unresolved_boundary`, `dead_end`, `cycle`, `truncated_depth`) permanecen en el core como enumeración abierta.
- **Evidencia primaria vs. derivado:** el camino en sí es **derivado** determinísticamente por el resolver a partir de `Call`/`DataOperation`/`Instantiation` primarios — es evidencia de segundo orden con provenance completa (`evidence_refs`), no evidencia inventada.

## FunctionalFlow

- **Propósito:** agrupa todos los `FunctionalPath` que nacen del mismo `EntryPoint`.
- **Identidad:** `FLOW-` preservado (V5.0 D-02, R0: 0/12 642). Fórmula confirmada: `_stable_id("FLOW", entry.id, entry.handler_method)` (poly33, no SHA-256 — nótese: a diferencia de `PATH-`, `FLOW-` sigue usando el hash poly33 heredado, no SHA-256; V5.0 D-02 decidió preservarlo tal cual sin re-derivar, y R0 confirma que 0 colisiones lo sostiene empíricamente sobre datos reales).
- **Campos mínimos:** `entry_point_id`, `path_ids[]` (derivable agrupando `FunctionalPath` por `flow_id` — confirmado, `functional_flows.json` V4.3 no tiene este campo hoy, R2/R3 lo señalan como GAP a añadir), `state`, `summary_counts`.
- **Campos opcionales:** campos de segmentación (§7 abajo, solo serializados con default neutro, sin lógica).
- **Relaciones:** `EntryPoint -> FunctionalFlow` (**1:0..1**); `FunctionalFlow -> FunctionalPath`; `FunctionalFlow -> FlowGraph` (embebido).
- **Cardinalidad:** confirmada.
- **Origen de datos:** `analysis/flow_resolver.py::resolve` (bucle principal).
- **Clasificación:** `CORE_ENTITY`. `webform`/`event`/`handler`/`start_method` (denormalización directa de `EntryPoint`, presentes hoy en el dict `flow`) → **no se duplican en el core**: son derivables de `EntryPoint` vía `entry_point_id` y deben quedar como `derived projection`/`extensions`, no como campos propios de `FunctionalFlow` (evita la duplicación que R3 §NORMALIZED EVIDENCE CONTRACT prohíbe explícitamente: "no duplicar como evidencia canónica algo derivable sin pérdida").
- **Evidencia primaria vs. derivado:** `path_ids`, `summary_counts`, `status`, `has_confirmed_terminal`/`has_unresolved_boundary` son 100% derivados de los `FunctionalPath` que agrupa — ninguno es evidencia primaria independiente.

## FlowGraph

- **Propósito:** el grafo de nodos/aristas de un `FunctionalFlow` — no derivable solo de la lista de `FunctionalPath` (confirmado empíricamente por R2: el grafo incluye nodos/aristas que ninguna reconstrucción de `paths` reproduce exactamente sin volver a caminar el árbol de llamadas).
- **Identidad:** embebida en `FunctionalFlow` (sin ID propio — es una propiedad estructural del flow, no una entidad direccionable independientemente).
- **Campos mínimos:** `nodes[]` (id, type, label, project — confirmado en código: `_node_impl`), `edges[]` (source, target, type, confidence, evidence_ref — confirmado: `_add_edge_impl`), `terminal_operations[]`.
- **Relaciones:** pertenece a exactamente un `FunctionalFlow`.
- **Origen de datos:** `analysis/flow_resolver.py` + `analysis/_flow_graph_construction.py`.
- **Clasificación:** `CORE_ENTITY` (embebida). Los tipos de nodo `WebForm`/`Handler`/`Event`/`Class`/`Project`/`DataAccessOperation`/`StoredProcedure` (confirmados en `_node` calls del código) son vocabulario de tecnología → mismo tratamiento que `terminal_type`: enumeración abierta, namespaced donde corresponda.
- **Evidencia primaria vs. derivado:** 100% derivado, con provenance íntegra vía `evidence_ref` por arista (confirmado: cada `_add_edge` recibe un `evidence_ref`, nunca `None` salvo los tres primeros edges estructurales del flow que referencian `entry.get("id")`).

## UnresolvedBoundary

- **Propósito:** un límite donde la resolución determinista no pudo continuar — concepto de primera clase, nunca un mero warning (V5.0 §NORMALIZED EVIDENCE CONTRACT, reafirmado aquí).
- **Identidad:** derivada de forma estable de `path_id` (+ `boundary_target`/`reason_code` si hace falta desambiguar más de un boundary por path) — **nunca `UNRES-`** (V5.0 DR-R2-01, R0 confirma 25 colisiones reales/216 172 sobre `UNRES-`). `path_id` en sí es único (R0: 162 914/162 914, mismo espacio de `PATH-`).
- **Campos mínimos:** `path_id`, `boundary_target` (= `terminal_target` del path), `reason_code` (deriva de `terminal_type`: `unresolved_boundary`|`cycle`|`truncated_depth`|`external_boundary`), `state` = **siempre** `"unresolved"`.
- **Campos opcionales:** `candidates[]` (solo si determinista — hoy `Call.candidates` existe para instanciaciones inferidas por tipo de variable, ver `call_extractor._call_from_match`).
- **Relaciones:** referenciada por `FunctionalPath` (es, en efecto, una vista filtrada de `FunctionalPath` con `terminal_type` en el conjunto de arriba — confirmado por R0/R2: `flow_unresolved.json` tiene contenido idéntico a ese filtro de `functional_paths.json`, pero con **orden de emisión distinto**, que debe preservarse por separado, no recomputarse).
- **Estados distinguidos (§8 más abajo):** el código actual (`flow_resolver`) solo produce dos valores de `confidence` reales en la práctica sobre datos IST: `"confirmed"` y `"unresolved"` (confirmado por R2 §D-06: "ningún `inferred` en IST real"). No existe un tercer estado `"unknown"` en el código actual ni evidencia de que se necesite — se documenta como posible pero **no se inventa**: `V5_1_R1_OPEN_DECISION` si algún adapter futuro (no VB/WebForms) sí lo necesitara.
- **Clasificación:** `CORE_ENTITY`.
- **Principio explícito preservado:** *ausencia de evidencia ≠ evidencia de ausencia* — un `UnresolvedBoundary` nunca se elimina ni se oculta por no tener `resolved_target`; su ausencia de resolución **es** el hecho a preservar, no un vacío a rellenar.

## EvidenceReference

Ver §6 (sección dedicada más abajo, con más detalle que la tabla resumen).

## ScanSummary

- **Propósito:** resumen agregado del SCAN (conteos, ignorados, snapshot de fuente) — proyección derivada, no evidencia primaria adicional.
- **Identidad:** ninguna (es un resumen singleton por corrida, no una colección de entidades).
- **Campos mínimos:** deriva de `EVIDENCE_MANIFEST.source_snapshot` (V5.0 §PERSISTENCE/CACHE BOUNDARY) + conteos por `file_type`.
- **Origen de datos:** hoy `repository.json` (`root`, `stats`, `ignored[]`, `duration_seconds`) producido en `cli/pipeline_stages.py`/scanner.
- **Clasificación:** `DERIVED_PROJECTION`. `duration_seconds` → `LEGACY_ONLY` (fuera de `evidence/`, excluido de D-01, confirmado en R0 como la única diferencia real de `repository.json` entre dos runs equivalentes).

---

# 4. IDENTIDAD

Tabla consolidada (idéntica en contenido a R3 §FINAL IDENTITY CONTRACT; repetida aquí con la fórmula de código verificada para cada una, que R3 no incluía a este nivel de detalle):

| Entity | Prefix | Fórmula confirmada en código | Fuente |
|---|---|---|---|
| `EntryPoint` | `EP-` | `_stable_id("EP", form_path, control, event, handler_name)` (poly33) | `web_entry_resolver.py:105` |
| `EventBinding` | `EVB-` | `_stable_id("EVB", form_path, control, event, handler_name)` (poly33) | `web_entry_resolver.py:88` |
| `FunctionalFlow` | `FLOW-` | `_stable_id("FLOW", entry.id, entry.handler_method)` (poly33) | `flow_resolver.py:48` |
| `DataOperation` | `DAO-` | `_stable_id("DAO", *operation_key)` (poly33, 11 campos) | `database_resolver.py:24` |
| `DataObject` (SP) | `SP-` | `_stable_id("SP", proc_name)` (poly33) | `database_resolver.py:35` |
| `DataObject` (SQL) | `SQL-` | `_stable_id("SQL", sql_operation, command_text, dynamic_sql)` (poly33) | `database_resolver.py:51` |
| `FunctionalPath` | `PATH-` | SHA-256 completo sobre JSON canónico de identidad | `flow_resolver.py:270-279` |
| `Project` | `PRJ-` (nuevo) | SHA-256(path normalizado) — **a implementar en R2**, no existe hoy | — |
| `Component` | `CMP-` (nuevo) | SHA-256(kind+source_ref+name+discriminador) — **a implementar en R2, discriminador `V5_1_R1_OPEN_DECISION`** | — |
| `ExternalDependency` | `XDP-` (nuevo) | SHA-256(kind+source+target+metadata) — **a implementar en R2** | — |
| `Call` | `CAL-` (nuevo) | SHA-256(file+line+expression+resolved_target+duplicate_ordinal) — **a implementar en R2, ordinal = posición en `calls[]` de su `SourceArtifact`** | — |
| `UnresolvedBoundary` | derivado de `path_id` (nuevo esquema) | a definir sobre `path_id`+`boundary_target`/`reason_code` — **a implementar en R2** | — |
| `DataParameter` | ninguna canónica | `legacy_ref` = `PAR-` (poly33, `_stable_id("PAR", *key)`) | `database_resolver.py:72` |
| `Call` legacy | ninguna canónica | `legacy_ref` = `CALL-` (poly33, transitorio, nunca persistido) | `flow_resolver.py:281-283` |
| `UnresolvedBoundary` legacy | ninguna canónica | `legacy_ref` = `UNRES-` (poly33, `_stable_id("UNRES", call_ref, expression)`) | `flow_resolver.py:152` |

No se convierte ningún ID en "texto arbitrario": cada `EP-`/`EVB-`/`FLOW-`/`DAO-`/`SP-`/`SQL-`/`PATH-` sigue siendo la identidad canónica de exactamente la entidad que produce (confirmado arriba, uno a uno), preservada bajo la condición de que el detector `id_unique_per_kind` (R3) siga confirmando 0 colisiones — condición ya verificada dos veces sobre datos reales (R2 sobre el despliegue IIS, R0 sobre el checkout de control de versiones, mismos resultados).

`PAR-`/`CALL-`/`UNRES-` permanecen como `legacy_ref`: nunca se usan como `id` de ninguna entidad V5, se preservan textualmente para trazabilidad y para no romper la proyección legacy `index/*.json`.

---

# 5. RELACIONES CRÍTICAS

| Relación | Cardinalidad | Directa/Derivada | Preservada de legacy / Reconstruida por adapter |
|---|---|---|---|
| `EntryPoint → FunctionalFlow` | **1 : 0..1** (no 1:1 — 20 EntryPoints sin flow, R0) | directa | preservada (ya es así en `flow_resolver`, solo entra `entry.confidence == "confirmed" and entry.handler_method`) |
| `EntryPoint → EventBinding` | 1 : 0..1 (misma tupla origen, pero registros independientes — ver nota) | directa | reconstruida: hoy `web_entry_resolver` genera ambas del mismo `event_data` en la misma pasada, pero como dos colecciones separadas sin arista explícita entre sus IDs |
| `FunctionalFlow → FunctionalPath` | 1 : N | directa | preservada (`path["flow_id"] = flow_id`, `flow_resolver.py:99`) |
| `FunctionalPath → Call` | N : N (vía `evidence_refs`) | derivada (evidence_refs apuntan a `legacy_ref` `CALL-`, no a `id` `CAL-`, hasta que R2 implemente `CAL-`) | reconstruida |
| `FunctionalPath → DataOperation` | 0..1 : 1 (terminal) | directa | preservada (`terminal_target`) |
| `FunctionalPath → UnresolvedBoundary` | 0..1 : 1 (cuando `terminal_type` unresolved-como) | directa (es una vista/reclasificación del mismo `FunctionalPath`, no una arista separada) | preservada, con orden propio (confirmado distinto del filtro naive, R0/R2) |
| `Project → Component` | 1 : N | derivada hoy (por `project_by_file`/namespace matching; nunca materializada como arista explícita en el código actual) | reconstruida por el adapter en R2 |
| `Component → Method` | 1 : N | derivada (símbolos con `members[]`, sin materializar `Method` como entidad hoy) | reconstruida |
| `Method → MethodReference` | 1 : N | pendiente de decisión (§2, `Method`) | pendiente |
| `Project → ExternalDependency` | N : N | derivada (hoy aristas `Dependency`) | reconstruida (CC-1 de R2/R3) |
| `DataOperation → DataObject` | N : 0..1 (terminal SP/SQL) | directa | preservada (`stored_procedure`/`sql_operation` en el dict de operación) |
| `DataOperation → DataParameter` | 1 : N | directa (composición) | preservada |

Todas las cardinalidades derivan de código real inspeccionado (`flow_resolver.py`, `web_entry_resolver.py`, `database_resolver.py`, `dependency_resolver.py`), no de suposición.

---

# 6. EvidenceReference

Contrato consolidado de R3, con el mapeo a evidencia real de código verificado en esta ronda:

```text
entity        {ref_type: "entity", entity_kind, entity_id}
source        {ref_type: "source", source_id, line?, excerpt?}
source_span   {ref_type: "source_span", source_id, start_line?, start_column?, end_line?, end_column?}   (reservado; V4.3 nunca produce columna — confirmado: `Evidence.line` es el único campo posicional en `models/evidence.py`, sin `column`)
textual       {ref_type: "textual", text, origin?}
```

`legacy_ref` (campo opcional adicional, no un `ref_type` propio): preserva `CALL-`/`PAR-`/`UNRES-`.

**Qué identifica:** una entidad concreta del modelo normalizado (`entity`), o una ubicación en el código fuente original con o sin fragmento (`source`), o una relación/hecho textual sin ID asociado (`textual`, p. ej. `dependencies.evidence` = `"InitializeComponent()"`, confirmado literal en `dependency_resolver._webform_deps`).

**Qué evidencia respalda:** `entity` respalda con la propia entidad ya validada (su `id` debe resolver en el store); `source`/`source_span` respaldan con la ubicación exacta en `SourceArtifact` (hoy `Evidence.file`+`Evidence.line`, confirmado en todos los extractores); `textual` respalda con una cita textual cuando no hay ID ni ubicación de línea disponible con la misma precisión (p. ej. el resumen agregado `functional_dependencies.evidence_samples`).

**Cómo se relaciona con una entidad:** toda entidad con `provenance` (campo común obligatorio, R3 §NORMALIZED EVIDENCE CONTRACT) lleva ≥1 `EvidenceReference`; toda promoción `unresolved → confirmed` (D-06) debe citar su `promotion_basis` con esta misma unión.

**Qué ocurre cuando no existe una referencia de fuente precisa:** se usa `textual` con el texto disponible, nunca se inventa un `source`/`entity` sin base — esto es exactamente la regla "no permitir que `EvidenceReference` se convierta en un mecanismo para inventar relaciones": un validador debe rechazar cualquier `EvidenceReference` cuyo `entity_id` no resuelva en el store o cuyo `source_id` no exista, marcándolo como **referencia rota** (fallo explícito de validación), nunca como referencia silenciosamente omitida.

**Cómo se evita que una proyección pierda trazabilidad:** toda proyección (`index/`, `documentation/`, `ai_context/`) hereda las `EvidenceReference` de la entidad que proyecta sin reescribirlas ni resumirlas a texto libre — si una proyección omite una entidad, debe declararlo en `omitted_*` (regla ya fijada en R3 §PROJECTION CONTRACT), nunca dejar una referencia colgando sin explicación.

---

# 7. FunctionalFlow / FunctionalPath — contrato ampliado con datos reales de R0

Usando los conteos reales de R0 sobre el target `C:\Users\cgalianj\source\IST_40\Operacional` (170 020 paths / 12 642 flows / 162 914 unresolved boundaries / 1 121 caminos a stored procedure / 1 a SQL / 4 612 a data operation / 1 372 dead-end / 0 cycle / 0 truncated / profundidad máxima observada 6 / profundidad media 1.3):

- **flow:** agrupación por `entry_point_id`; `state` = peor caso entre sus `path`s (`_weakest`, confirmado en código: cualquier path `unresolved` degrada todo el flow — y **por diseño ya preserva dos hechos adicionales independientes** `has_confirmed_terminal`/`has_unresolved_boundary`, añadidos en V4.2-R7.1 precisamente para que un flow con un terminal confirmado real no pierda esa información al agregarse con otro path no relacionado que sí es unresolved — patrón que V5.1 **debe preservar**, no colapsar).
- **path:** secuencia de nodos con `relation_types` paralelo, terminal tipado, `state`, `depth` (máximo observado 6 — la profundidad real de IST es baja, lo cual es información útil para dimensionar `max_depth` de futuros adapters, aunque V5.1 no cambia el valor por defecto actual de `flow_resolver`, que es 12).
- **depth:** `len(nodes) - 1`, siempre derivable, nunca almacenado independientemente de `nodes` (evita divergencia).
- **terminal:** uno de `{stored_procedure, sql, data_operation, unresolved_boundary, dead_end, cycle, truncated_depth, external_boundary}` — de estos, `external_boundary` aparece en el código (`flow_resolver.py:101`, en el filtro de `unresolved`) pero R0 midió **0 external_boundary** en el target real; se mantiene en la enumeración porque el código lo produce, aun sin evidencia actual de uso.
- **unresolved boundary:** ver §8.
- **data access / stored procedure / SQL:** terminal directo de un path, vía `DataOperation`→`DataObject`.
- **dependencies:** `FunctionalPath` no referencia `dependencies.json`/`functional_dependencies.json` directamente — esas son vistas derivadas independientes (D-04/DR-R2-02), no parte del contrato de `FunctionalPath` en sí.
- **calls:** vía `evidence_refs` (hoy `legacy_ref` `CALL-`, mañana potencialmente `entity` `CAL-` una vez R2 implemente la identidad nueva).
- **evidence refs:** cada arista del `FlowGraph` lleva su propio `evidence_ref` (confirmado, nunca `None` salvo las tres aristas estructurales iniciales del flow que usan el `id` del propio `EntryPoint`, lo cual es correcto: esas aristas SON evidenciadas por el propio `EntryPoint`).

**No se introduce segmentación avanzada en V5.1** (confirmado, fuera de alcance). El diseño es compatible con V5.6 porque `FunctionalFlow` reserva, solo serializados con default neutro (sin lógica): `parent_flow_id` (null), `segment_id` (null), `partial` (false), `included_paths[]` (vacío — nótese: **no** se usa como campo activo; `path_ids[]` completo sigue siendo la fuente de verdad hasta V5.6), `omitted_paths[]` (vacío), `evidence_refs[]` (vacío), `segment_reason` (null). Estos campos no se proyectan en `functional_flows.json` legacy (D-01, confirmado: el formato V4.3 no tiene ninguno de ellos).

---

# 8. UnresolvedBoundary — estados

El código actual (confirmado, no asumido) distingue exactamente dos estados de confianza en datos reales de IST: `confirmed` y `unresolved`. Un tercer estado `unknown` **no existe** en ningún resolver actual ni tiene evidencia de necesidad en R0/R2 — no se introduce (`V5_1_R1_OPEN_DECISION`, no una decisión tomada: queda documentado como posible extensión de un adapter futuro no-VB, nunca como parte del contrato mínimo de V5.1).

Reglas del contrato, sin cambios respecto a V5.0 D-06/R3, aplicadas aquí a `UnresolvedBoundary` específicamente:

- Un `UnresolvedBoundary` nunca se convierte en `confirmed` solo porque exista un texto parcial o un `candidate` inferido por tipo de variable (`Call.candidates`, ver `call_extractor._call_from_match`) — un `candidate` es información adicional que un consumidor humano/IA puede usar para *interpretar*, nunca una promoción automática de estado.
- **Ausencia de evidencia ≠ evidencia de ausencia:** un método que no aparece en `data_by_method`/`method_calls` no significa "este método no accede a datos/no llama a nada" — significa "el resolver determinista no encontró evidencia suficiente", y el contrato preserva esa distinción marcando el path como `dead_end` (sí explorado, sin operación encontrada) en vez de simplemente omitirlo. Confirmado en código: `flow_resolver.py:158-159`, `if not data_ops and not followed: self._add_path(..., "dead_end", ...)` — el dead-end es un hecho de primera clase, no un vacío.

---

# 9. ADAPTER BOUNDARY

El core normalizado (`evidence/`, entidades §2-3) no debe depender directamente de VB.NET, WebForms, `.vbproj`, archivos específicos, reglas de un parser concreto, o estructuras internas de V4.x. Verificación concreta sobre el código real inspeccionado en esta ronda:

| Módulo actual | Pertenece a | Por qué |
|---|---|---|
| `extractors/vbnet_extractor.py`, `extractors/webforms_extractor.py`, `extractors/vbproj_extractor.py`, `extractors/web_event_extractor.py`, `extractors/webconfig_extractor.py`, `extractors/solution_extractor.py`, `extractors/call_extractor.py`, `extractors/database_extractor.py` + `_database_*` | **Technology Adapter** (`vbnet-webforms-oracle`) — Source discovery + Extraction (responsabilidades 1-2 de R3 §FINAL ADAPTER CONTRACT) | Todos son parsers/regex específicos de VB.NET, sintaxis WebForms, XML de `.vbproj`/`Web.config`, y patrones SQL/ADO.NET — exactamente el vocabulario que el core debe evitar. |
| `analysis/call_resolver.py`, `analysis/web_entry_resolver.py`, `analysis/database_resolver.py`, `analysis/dependency_resolver.py` | **Technology Adapter** — Technology-specific/Database-specific normalization (responsabilidades 3-4) | Consumen los dicts crudos de los extractores y producen las estructuras actuales (`EntryPoint`, `Call` resuelto, `DataOperation`, `Dependency`); son el punto donde V5.1 debe envolver, no reescribir (D-04), para producir entidades `evidence/` neutrales. |
| `analysis/flow_resolver.py` (+ `_flow_graph_construction.py`, `_flow_key_labels.py`, `_flow_report_composition.py`) | **Core** (resolver de flows, R3: "consume solo entidades normalizadas") | Ya opera sobre estructuras razonablemente neutrales (`method_key` tuplas, no clases VB); su entrada debe migrar a `Component`/`Call`/`DataOperation` normalizados en vez de los dicts crudos actuales, pero su lógica de recorrido de grafo no es específica de VB.NET. |
| `legacy_documenter/models/*` | **Mixto** — `Evidence` es reutilizable como base de `EvidenceReference{ref_type: source}` (core); `EntryPoint`/`EventBinding`/`Call`/`Instantiation`/`Project`/`SourceFile`/`Symbol`/`WebForm`/`Dependency` son el punto de partida de las entidades `evidence/`, pero hoy mezclan campos core con campos de vocabulario (p. ej. `Project.target_framework`) — R2 debe separar cada dataclass en `{campos core} + extensions[adapter_id]`. |
| `legacy_documenter/utils/atomic_write.py` | **Core** (utilidad de persistencia, tecnología-agnóstica) | Ya es agnóstica; usada tal cual por `evidence/` en R2. |
| `legacy_documenter/exporters/json_exporter.py`, `markdown_exporter.py`, `technical_documentation_renderer.py` | **Legacy Compatibility Projection** (D-04) | Producen `index/`/`documentation/` V4.3; en V5.1 deben leer de `evidence/` en vez de directamente de los resolvers (cambio de fuente, no de forma — D-01 exige que su salida no cambie). |

Información específica de tecnología que no puede entrar al core (namespace VB.NET, directivas WebForms, `target_framework`/`.vbproj`, `provider`/`command_type` ADO.NET, `type_guid`/`guid` de `.sln`, atributos de `Web.config`) se conserva íntegra en `extensions["vbnet-webforms-oracle"]`, namespaced, nunca leída por el core (regla ya fijada en R3, reafirmada aquí sin cambios).

---

# 10. LEGACY COMPATIBILITY

```text
Normalized Evidence → Legacy Compatibility Projection → V4-compatible index representation
```

Dirección confirmada como no-invertible con evidencia de código: hoy (V4.3) `index/*.json` **es** producido directamente por los resolvers (`JSONExporter().export(output, indexes)` en `pipeline_stages.export_artifacts`, donde `indexes` es el dict que los resolvers ya devuelven). V5.1 R2 debe insertar `evidence/` **entre** los resolvers y `JSONExporter`, de modo que `JSONExporter` pase a leer de una proyección construida desde `evidence/`, no de los resolvers directamente — sin cambiar ni una clave, ni un orden, ni un valor de lo que hoy produce (D-01, D-04). `index/` no se convierte en fuente de verdad: sigue siendo, después de R2, exactamente lo que es hoy desde el punto de vista de cualquier consumidor externo (byte-idéntico sobre el mismo input, confirmado viable por R0/R2), pero internamente pasa a ser una **proyección regenerable**, no el único lugar donde el conocimiento vive.

---

# 11. PERSISTENCE CONTRACT

Sin cambios de fondo respecto a R3 §FINAL PERSISTENCE/CACHE BOUNDARY (D-03, D-05); aplicado aquí con lo que el código actual ya ofrece o no:

- **Canónico:** `evidence/` — todavía no existe físicamente; V5.1 R2 lo crea. Contiene las entidades §2-3.
- **Compatibilidad:** `index/` — existe hoy, producido directamente; pasa a ser regenerado desde `evidence/`.
- **Puede regenerarse:** `index/`, `documentation/`, `ai_context/`, `consumer_projection/`, `RUN_SUMMARY.*` — ninguno de ellos requiere volver a ejecutar SCAN/EXTRACTION/resolución si `evidence/` ya existe (D-03).
- **No debe perderse:** todo campo primario listado como tal en §2-3 (identidades preservadas, `evidence`/`EvidenceReference`, `state`, `UnresolvedBoundary`, `legacy_ref`).
- **Identificadores estables:** los 7 prefijos legacy preservados (§4) + los 4 nuevos una vez asignados en R2 (asignación determinista sobre clave natural — no cambian entre corridas del mismo input, ya que SHA-256 sobre datos deterministas es en sí determinista).
- **Relaciones reconstruibles:** todas las de §5, a partir de las entidades persistidas — ninguna relación depende de estado en memoria no persistido (confirmado: hoy `flow_resolver` reconstruye todo su índice `method_calls`/`data_by_method` desde los dicts de entrada en cada `resolve()`, sin estado oculto entre llamadas — buena señal de que la migración a `evidence/` no encuentra un obstáculo de estado implícito).

Formato físico: sin decisión nueva respecto a R3 (JSONL particionado, recomendado, no fijado hasta que R2 lo mida — fuera de alcance de R1 implementarlo).

---

# 12. INVARIANTES (contrato de test para R2)

| # | Invariante | Verificable sobre |
|---|---|---|
| I-1 | `id_unique_per_kind` — 0 colisiones para `{EP, EVB, FLOW, DAO, SP, SQL, PATH, PRJ, CMP, XDP, CAL}` + identidad de `UnresolvedBoundary` | índices reales (ya confirmado 2 veces para los 7 legacy, R2+R0; pendiente para los 5 nuevos hasta que R2 los implemente) |
| I-2 | `PAR/CALL/UNRES` nunca aparecen como `id` de ninguna entidad V5, solo como `legacy_ref` | schema de cada entidad + grep del código de persistencia |
| I-3 | `entry_point_to_flow_cardinality` — `0..1`, nunca asumir `1` | conteo `EntryPoint` vs `FunctionalFlow` (ya confirmado 12 662 vs 12 642 dos veces) |
| I-4 | Trazabilidad — toda entidad con `provenance` resuelve a ≥1 `EvidenceReference` válida | recorrido del store completo |
| I-5 | `evidence_reference_resolves_or_fails_explicitly` — ninguna referencia rota pasa silenciosamente | validador dedicado sobre `evidence/` completo |
| I-6 | No invención — una proyección no crea relaciones/entidades ausentes de `evidence/` | comparación de conjuntos de IDs citados en cada proyección vs. `evidence/` |
| I-7 | `no_promotion_without_basis` — ningún `unresolved → confirmed` sin `promotion_basis` citado | recorrido de `state`+`promotion_basis` |
| I-8 | `state_immutable_across_projections` — `state` de una entidad es idéntico en `evidence/`, `index/`, `documentation/`, `ai_context/` | comparación cruzada |
| I-9 | `legacy_projection_byte_equivalence` — `index/*.json` byte-idéntico a V4.3 sobre el mismo input (ya heredada de D-01/R1) | fixtures + IST real |
| I-10 | Determinismo — la misma evidencia de entrada produce la misma evidencia normalizada (dos builds consecutivos, mismo input) | `evidence/` reconstruido dos veces |
| I-11 | `included ∩ omitted = ∅` para campos de segmentación (aunque no tengan lógica activa en V5.1, deben serializarse consistentemente con sus defaults) | schema de `FunctionalFlow` |

---

# 13. MAPPING V4.3 → V5.1

Solo conceptos con evidencia real (código y/o R0); sin mappings especulativos.

| V4.3 source/index | V5.1 normalized entity | Clasificación | Identidad | Transformación |
|---|---|---|---|---|
| `scanner/repository_scanner.py` → `files.json` (`SourceFile`) | `SourceArtifact` | `CORE_ENTITY` | `SRC-`+SHA-256(path) (nuevo) | añade `sha256` (dato nuevo); resto preservado |
| `extractors/solution_extractor.py` → `solutions.json` | `Solution` | `CORE_RELATION` + `ADAPTER_EXTENSION` | `V5_1_R1_OPEN_DECISION` (¿`SOL-`?) | `type_guid`/`guid` → extensions |
| `extractors/vbproj_extractor.py` → `projects.json` (`Project` model) | `Project` | `CORE_ENTITY` | `PRJ-` (nuevo) | `target_framework`/`root_namespace`/`assembly_name`/`configurations` → extensions |
| `extractors/vbnet_extractor.py` → `symbols.json` (`Symbol` model) | `Component` (fusionado con `WebForm`) | `CORE_ENTITY` + `ADAPTER_EXTENSION` | `CMP-` (nuevo, discriminador pendiente) | `namespace_confidence` → `state`; `modifiers`/`inherits`/`implements` → extensions |
| `extractors/webforms_extractor.py` → `webforms.json` (`WebForm` model) | `Component` (mismo, `component_kind` WebForms) | `CORE_ENTITY` + `ADAPTER_EXTENSION` | `CMP-` (mismo esquema) | `directives`/`codebehind`/`registers`/`scripts`/`stylesheets`/`markup_events` → extensions |
| `analysis/web_entry_resolver.py` → `entry_points.json` (`EntryPoint` model) | `EntryPoint` | `CORE_ENTITY` + `ADAPTER_EXTENSION` (valores) | `EP-` (preservado) | `outgoing_calls[]` → `Call.owner_entry_point_id` (relación, no campo embebido) |
| `analysis/web_entry_resolver.py` → `event_bindings.json` (`EventBinding` model) | `EventBinding` | `CORE_ENTITY` + `ADAPTER_EXTENSION` | `EVB-` (preservado) | sin cambio estructural |
| `extractors/call_extractor.py` + `analysis/call_resolver.py` → `calls.json` (`Call` model) | `Call` | `CORE_ENTITY` + `ADAPTER_EXTENSION` | `CAL-` (nuevo); `CALL-` → `legacy_ref` | añade `duplicate_ordinal`; `receiver`/`receiver_path` → extensions |
| `extractors/call_extractor.py` (`Instantiation` model) | `Instantiation` | `CORE_ENTITY` | sin ID propio (posicional) | sin cambio estructural, solo se materializa como partición propia de `evidence/` |
| `extractors/call_extractor.py` (`TypeReference`/import) | `Import` | `ADAPTER_EXTENSION` (de `Component`/`SourceArtifact`) | sin ID propio | específico de VB `Imports` |
| `analysis/database_resolver.py` → `data_access.json` | `DataOperation` | `CORE_ENTITY` + `ADAPTER_EXTENSION` | `DAO-` (preservado) | `provider`/`access_kind`/`command_*`/`wrapper` → extensions |
| `analysis/database_resolver.py` → `stored_procedures.json`/`sql_operations.json` | `DataObject` | `CORE_ENTITY` | `SP-`/`SQL-` (preservados) | sin cambio |
| `analysis/database_resolver.py` → `data_parameters.json` | `DataParameter` | `CORE_ENTITY` | sin canónica; `PAR-` → `legacy_ref` | sin cambio estructural |
| `analysis/database_resolver.py` → aristas `CONN-` en `dependencies.json` | `ExternalDependency` (tipo store) — **`V5_1_R1_OPEN_DECISION`** | `CORE_ENTITY` (tentativo) | `XDP-` (tentativo) | sin precedente claro en V5.0/R2/R3 — R2 debe decidir con evidencia |
| `dependency_resolver.py` → aristas `Project -> DLL` en `dependencies.json` | `ExternalDependency` | `CORE_ENTITY` | `XDP-` (nuevo) | materializar entidad propia en vez de arista genérica `Dependency` |
| `analysis/flow_resolver.py` → `functional_paths.json` | `FunctionalPath` | `CORE_ENTITY` | `PATH-` (preservado) | sin cambio estructural; `nodes[]` gana referencia tipada si R2 resuelve `Method` |
| `analysis/flow_resolver.py` → `functional_flows.json` | `FunctionalFlow` + `FlowGraph` embebido | `CORE_ENTITY` | `FLOW-` (preservado) | añade `path_ids[]` (derivado); `webform`/`event`/`handler`/`start_method` pasan a derivados de `EntryPoint`, no campos propios |
| `analysis/flow_resolver.py` → `flow_unresolved.json` | `UnresolvedBoundary` | `CORE_ENTITY` | derivada de `path_id` (nuevo esquema); `UNRES-` → `legacy_ref` | vista con orden propio preservado |
| `analysis/flow_resolver.py` → `flow_summary.json` | (resumen) | `DERIVED_PROJECTION` | n/a | recomputable |
| `analysis/dependency_resolver.py` → `dependencies.json` | `Project.dependencies[]` / `ExternalDependency` (relación) | `DERIVED_PROJECTION` | n/a | orden propio persistido (no recomputable por clave simple, confirmado R0) |
| (derivado en `ai_projection`/consumer, no en resolvers) → `functional_dependencies.json` | (vista) | `DERIVED_PROJECTION` | n/a | orden propio a fijar en R2 |
| `extractors/webconfig_extractor.py` → `configuration.json` | `ConfigurationEntry` | `ADAPTER_EXTENSION` (de `SourceArtifact`) | sin ID propio | íntegro en extensions |
| `cli/pipeline_stages.py` (SCAN) → `repository.json` | `ScanSummary` | `DERIVED_PROJECTION` | n/a | `duration_seconds` → `LEGACY_ONLY` |

---

# 14. IMPACT ANALYSIS (para R2 — no se modifica código en esta ronda)

| Componente | Clasificación |
|---|---|
| `legacy_documenter/models/*` | `MODIFY` — separar campos core de campos de vocabulario; añadir `SourceArtifact`, `Component`, `Solution`, `ExternalDependency`, `DataObject`, `UnresolvedBoundary`, `EvidenceReference` como dataclasses nuevas |
| `legacy_documenter/extractors/*` | `REUSE` — ninguno cambia su lógica de extracción (D-04: "envolver, no reescribir") |
| `legacy_documenter/analysis/{call_resolver,web_entry_resolver,database_resolver,dependency_resolver}.py` | `ADAPTER` — se convierten en la implementación del Technology Adapter de referencia; su salida se envuelve para producir entidades `evidence/` en vez de (o además de) los dicts actuales |
| `legacy_documenter/analysis/flow_resolver.py` (+ helpers) | `ADAPTER` en el corto plazo (aún consume dicts con vocabulario WebForms en `terminal_type`/nodos), con un núcleo de recorrido de grafo que `REUSE` puede conservar en gran parte |
| `legacy_documenter/exporters/{json_exporter,markdown_exporter,technical_documentation_renderer}.py` | `MODIFY` — cambiar su fuente de datos (leer de `evidence/`/proyección en vez de resolvers directos), sin cambiar su salida (D-01) |
| `legacy_documenter/utils/atomic_write.py` | `REUSE` — ya es la primitiva de persistencia agnóstica que `evidence/` necesita |
| `legacy_documenter/cli/pipeline_stages.py` | `MODIFY` — insertar la construcción/persistencia de `evidence/` entre la resolución y `EXPORT` |
| `legacy_documenter/context/{consumer_projection,hydration,ai_projection,context_builder,system_context_builder}.py` | `MODIFY` (más adelante, no necesariamente en el primer corte de R2) — hoy leen del dict legacy `ix`/`index/`; su migración a leer `evidence/` es D-08-compatible pero no obligatoria para el primer round de R2 |
| `legacy_documenter/knowledge/*` (approval, proposals, canonical, provenance) | `OUT_OF_SCOPE` — pertenecen a V5.7 (Approval/Canonical), fuera de V5.1 |
| `legacy_documenter/llm/*` | `OUT_OF_SCOPE` — provider genérico es V5.5 |
| `legacy_documenter/documentation/{generator,hierarchical,resume,systematic,human_review,second_review}.py`, `knowledge/readiness.py`/`closure/*` | `DEPRECATE_LATER` — legacy congelado / tooling de desarrollo (R3 §FINAL RUNTIME/TOOLING BOUNDARY), sin cambios en V5.1 |
| `tests/*` | `MODIFY` (en R2, no en R1) — necesitan cobertura nueva para `evidence/`, sin tocar los tests existentes de `index/` (deben seguir pasando byte a byte) |

---

# 15. TEST CONTRACT PARA R2

| Categoría | Qué debe demostrar |
|---|---|
| **unit tests** | Cada entidad nueva (`SourceArtifact`, `Component`, `ExternalDependency`, `DataObject`, `UnresolvedBoundary`, `EvidenceReference`) serializa/deserializa correctamente; cada fórmula de ID nueva (`PRJ-`, `CMP-`, `XDP-`, `CAL-`, identidad de `UnresolvedBoundary`) es determinista sobre la misma entrada. |
| **contract tests** | Las 11 invariantes de §12 (I-1…I-11), cada una como test explícito y nombrado igual que en esta tabla, para trazabilidad directa contrato↔test. |
| **real IST regression** | Ejecutar sobre el target real de R0 (`C:\Users\cgalianj\source\IST_40\Operacional`, o su sucesor si cambia) — no solo fixtures pequeños: `id_unique_per_kind` sobre los ≥170 000 `FunctionalPath`/≥230 000 `Call` reales; verificar que `evidence/` reconstruido desde este target reproduce los mismos conteos que R0 documentó (12 662 EP, 12 642 FLOW, 20 082 DAO, etc.). |
| **legacy compatibility regression** | `legacy_projection_byte_equivalence` (I-9) sobre fixtures (`v2_r1_sample`, `v4_2_r3_sample`, `v4_2_r7_full_sample`, ya usados en R1/R2) + comparación SHA-256 por índice contra el `OUTPUT_MANIFEST.json` de una corrida IST real, exactamente como R0 lo hizo manualmente esta ronda (ahora como test automatizado repetible). |
| **determinism checks** | I-10: reconstruir `evidence/` dos veces sobre el mismo input, comparar byte a byte. |
| **identity checks** | I-1, I-2, I-3: detector de colisiones + verificación de que `PAR/CALL/UNRES` nunca aparecen como `id`. |
| **traceability checks** | I-4, I-5, I-6, I-7, I-8: recorrido completo del store verificando que toda entidad resuelve a evidencia, ninguna referencia rota pasa en silencio, ninguna proyección inventa relaciones ni cambia `state` sin `promotion_basis`. |

Explícito, sin ambigüedad: **no usar únicamente fixtures pequeños** — I-9/real IST regression exige ejecutar sobre datos reales a la escala medida en R0 (cientos de miles de registros), no solo sobre los fixtures de decenas/cientos de registros que hoy cubren `tests/fixtures/`.

---

# 16. COMPATIBILIDAD V5.2 / V5.5

```text
Normalized Evidence → AI factual interpretation → Audience transformation → Profile → Template → Renderer
Normalized Evidence → Generic AI Provider
```

V5.1 no se acopla a ningún provider de IA ni a ningún motor de templates — confirmado por diseño: ninguna entidad de §2-3 referencia `legacy_documenter.llm.*`, y el único punto donde IA participa hoy (`orchestration/ai_interpretation.py`) consume `ai_context/` (una proyección, no `evidence/` directamente), consistente con R3 §FINAL PROVIDER CONTRACT ("ninguna brecha exige tocar evidence ni selection"). `EvidenceReference{ref_type: entity}` (§6) es exactamente lo que D-16/R3 exige para que las `proposals` de V5.7 y el futuro Profile `ai-context` de V5.2 tengan grounding verificable sin que V5.1 tenga que anticipar su lógica de selección/budget (que permanece, sin cambios, en `select_flow_ids`/`AiProjectionBuilder.package`/`measure_request_payload`, D-08).

---

# 17. CRITERIO DE CIERRE — verificación

| Elemento exigido | ¿Definido en este documento? |
|---|---|
| Modelo de entidades | Sí, §2-3 (19 conceptos, cada uno con las 10 dimensiones pedidas) |
| Identidad | Sí, §4 (tabla consolidada + fórmulas de código verificadas) |
| Relaciones | Sí, §5 (12 relaciones mínimas + cardinalidad + directa/derivada/preservada/reconstruida) |
| EvidenceReference | Sí, §6 |
| Unresolved | Sí, §8 |
| Adapter boundary | Sí, §9 (tabla módulo por módulo) |
| Legacy compatibility | Sí, §10 |
| Persistence boundary | Sí, §11 |
| Invariantes | Sí, §12 (11 invariantes verificables) |
| Mapping V4.3 → V5.1 | Sí, §13 (24 filas, todas con respaldo de código/R0, ninguna especulativa) |
| Impacto de implementación | Sí, §14 |
| Contrato de tests R2 | Sí, §15 |
| Compatibilidad V5.2/V5.5 | Sí, §16 |

**No existe contradicción real con V5.0**: cada decisión de este documento aplica, detalla o mide empíricamente una decisión ya aprobada en `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`; ninguna la contradice. Por tanto no se declara `V5_1_R1_CONTRACT_CONFLICT`.

**Decisiones abiertas identificadas (no resueltas silenciosamente):**

1. `V5_1_R1_OPEN_DECISION` — identidad de `Solution` (¿`SOL-`? R2 debe confirmar si algún consumidor la necesita).
2. `V5_1_R1_OPEN_DECISION` — identidad/entidad de `Method`: ¿ID propio (`MTH-`) o permanece como referencia estructural sin entidad? Bloqueado por falta de medición de colisiones `(class, method)` en datos reales.
3. `V5_1_R1_OPEN_DECISION` — discriminador determinista exacto para el desempate de `Component` (`CMP-`) ante el duplicado real conocido `(file, name, kind)`.
4. `V5_1_R1_OPEN_DECISION` — tratamiento de `CONN-` (conexión de datos, hoy arista `DataAccessOperation -> Connection` sin mención previa en V5.0/R2/R3): ¿es `ExternalDependency` de tipo store, o necesita su propio concepto?
5. `V5_1_R1_OPEN_DECISION` (menor) — si `UnresolvedBoundary`/otras entidades de un adapter futuro no-VB necesitarán alguna vez un tercer estado `unknown`, distinto de `confirmed`/`unresolved`.

Ninguna de estas decisiones abiertas bloquea el cierre de R1 (no son contradicciones, son huecos de evidencia insuficiente para decidir sin inventar); todas quedan explícitamente para R2, que debe resolverlas con medición adicional antes de fijar el schema físico definitivo, no por diseño especulativo.

---

# RESTRICCIONES CONFIRMADAS

No se implementó V5.1. No se modificó producción, tests ni `PROJECT_STATE.json`. No se ejecutó IA real. No se cambió V5.0 ni el roadmap. No se introdujeron templates, providers, cache, ni segmentación con lógica activa (solo campos reservados con default neutro, ya autorizado explícitamente por el prompt de esta ronda). No se creó código provisional ni fixtures nuevos. No se creó ningún otro `.md`.

## FILES READ

`CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`, `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`, `docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md`, `docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md`, `docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md`; código: `legacy_documenter/models/{evidence,entry_point,call,project,source_file,symbol,webform,dependency}.py`, `legacy_documenter/analysis/{flow_resolver,database_resolver,web_entry_resolver,dependency_resolver}.py`, `legacy_documenter/extractors/{solution_extractor,webconfig_extractor,call_extractor}.py`, `legacy_documenter/utils/atomic_write.py`, `legacy_documenter/context/consumer_projection.py`, `legacy_documenter/context/hydration.py` (parcial), `legacy_documenter/cli/pipeline_stages.py` (parcial, ya leído en rondas previas de esta sesión).

## FILES MODIFIED

- Creado: `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`.
- Ningún otro archivo del repositorio modificado.
