# V5.0 R2A — Contract Corrections

## STATUS

`V5_0_R2A_CONTRACT_CORRECTIONS_READY`

Ronda documental / corrección de contrato. No se modificó producción, tests, CLI, providers, `PROJECT_STATE.json` ni ningún artefacto fuera de este documento. No se ejecutó IA real ni un `full` IST. No se crea R3: queda pendiente de revisión/aprobación humana antes de iniciarla.

Esta ronda resuelve los 4 `CONTRACT_CONFLICT` (CC-1…CC-5, agrupados en DR-R2-01…04) que dejaron `docs/V5/V5_0_R2_CONTRACT_VALIDATION.md` en `V5_0_R2_CONTRACT_CHANGES_REQUIRED`, y fija formalmente la resolución de los 4 tests rojos (Opción A). Las decisiones D-01…D-16 de `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md` no se renumeran; donde R2A las corrige, quedan registradas como `D-xx Amendment R2A` sin perder su identificador original.

## EXECUTIVE SUMMARY

R2A aprueba y formaliza las cuatro Decision Records propuestas por R2 (DR-R2-01…04), con el detalle y la nomenclatura exigidos por el prompt de esta ronda, y fija la resolución de los tests rojos como decisión contractual (sin tocar tests todavía). En síntesis:

- **DR-R2-01 (identidades):** `EP-`, `EVB-`, `FLOW-`, `DAO-`, `SP-`, `SQL-`, `PATH-` quedan confirmados como identidad V5 persistida (0 colisiones medidas en IST). `PAR-`, `CALL-`, `UNRES-` dejan de ser identidad canónica V5 y pasan a `legacy_ref` (colisiones reales: 5/27/25). `Project`, `Component`, `ExternalDependency`, `Call` reciben IDs V5 nuevos (`PRJ-`, `CMP-`, `XDP-`, `CAL-`) por SHA-256 completo sobre clave natural; `UnresolvedBoundary` recibe identidad V5 derivada de forma estable de `path_id`, no de `UNRES-`. `EntryPoint → FunctionalFlow` pasa de `1:1` a `1:0..1` (20 EntryPoints unresolved sin flow).
- **DR-R2-02 (evidencia normalizada):** se completa la tabla de entidades de R1 con los 12 grupos de campos sin destino, clasificando cada uno como core entity, core relation, adapter extension, derived projection o legacy-only field.
- **DR-R2-03 (observabilidad):** D-12 se corrige. `RUN_SUMMARY.json` permanece byte-determinista y sin campos nuevos; la observabilidad pasa a un sidecar aditivo `RUN_OBSERVABILITY.json`, fuera de D-01, con campos clasificados `required`/`optional`/`diagnostic`.
- **DR-R2-04 (EvidenceReference):** se reemplaza la definición contradictoria de R1 por una unión etiquetada `ref_type ∈ {entity, source, source_span, textual}` + `legacy_ref` opcional.
- **Tests rojos:** se fija la Opción A recomendada por R2 como decisión contractual. R2A no modifica ningún test; la corrección física queda para una ronda posterior autorizada explícitamente.

Con estas cuatro correcciones incorporadas, el contrato de V5.0 queda sin conflictos abiertos entre D-01…D-16 y en condiciones de que una ronda posterior (no autorizada por R2A) consolide el paquete final y decida si V5.1 puede comenzar.

## APPROVED DECISION RECORDS

### DR-R2-01 — Identidades y colisiones (APROBADO)

**Problem:** R1 asignaba "ID V4.3" como identidad canónica a `Project`, `Component`, `ExternalDependency`, `Call` y `UnresolvedBoundary`, pero ninguno de los cinco tiene, en V4.3, un ID persistido y estable; y R1 asumía `EntryPoint → FunctionalFlow` como `1:1`.

**Decision:**

1. **IDs legacy preservados como identidad V5** (0 colisiones medidas en IST — `EP-`, `FLOW-`, `DAO-`, `PATH-`; y 0 colisiones adicionales verificadas para `EVB-`, `SP-`, `SQL-`): `EP-`, `EVB-`, `FLOW-`, `DAO-`, `SP-`, `SQL-`, `PATH-`. Se mantienen sin cambios como `id` de la entidad normalizada correspondiente, sujetos al detector `id_unique_per_kind` (D-02).
2. **IDs legacy NO únicos / NO persistidos como identidad**: `PAR-` (5 colisiones/74 633), `CALL-` (27 colisiones + 1 383 duplicados de tupla/230 356), `UNRES-` (25 colisiones/216 172 derivados). Dejan de tratarse como identidad canónica V5. Se conservan como campo `legacy_ref` (ver DR-R2-04) para compatibilidad y trazabilidad legacy. No se renombran ni migran retroactivamente; el detector de colisiones no los cubre como identidad de entidad.
3. **Nuevas identidades V5** para entidades sin ID persistido/estable en V4.3, por SHA-256 completo sobre JSON canónico de su clave natural:
   - `Project → PRJ-` — clave natural: `path` normalizado (259/259 únicos; `name` no lo es, 218/259).
   - `Component → CMP-` — clave natural: `kind + source artifact + name` + discriminador determinista si hace falta (símbolos: 6 512/6 513 únicos por `(file, name, kind)`; 1 duplicado real conocido en `cc\cc\ccTMP.vb`/`ccRma1` requiere el discriminador).
   - `ExternalDependency → XDP-` — clave natural: `tipo + source + target + metadata mínima estable` (hoy embebida en aristas de `dependencies`/`assembly_references`, sin ID propio).
   - `Call → CAL-` — clave natural: `source artifact + containing symbol + line + expression` + **duplicate ordinal determinista** (necesario: 1 383 registros comparten tupla idéntica). El ordinal no se basa en orden de iteración no determinista; se deriva de un criterio estable declarado por el store (p. ej. posición dentro de la lista `calls[]` del archivo tal como la emite el extractor, que es determinista por artefacto).
   - `UnresolvedBoundary` — identidad V5 derivada de forma estable de `path_id` (terminal, único: 162 914/162 914), combinado con `boundary type/target` cuando haga falta desambiguar más de un boundary por path. No depende de `UNRES-`.
4. **`EntryPoint → FunctionalFlow`**: se corrige de `1:1` a **`1:0..1`**. Evidencia: 12 662 `EntryPoint` vs 12 642 `FunctionalFlow`; 20 EntryPoints `unresolved` con `handler_method=null` no generan flow.

**Rationale:** los IDs poly33 de 10 dígitos (`~10^9` de espacio) no son identidad fiable para tipos de alta cardinalidad (`PAR-` 74 633, `CALL-`/`UNRES-` >200 000); los cinco tipos sin ID V4.3 nunca tuvieron una identidad persistida que re-derivar, así que asignarles ID V5 nuevo no rompe compatibilidad (no hay nada que romper). Cambiar `EP:FLOW` a `1:0..1` documenta un hecho ya presente en los datos, no un cambio de comportamiento.

**Alternatives rejected:** re-derivar `EP/FLOW/DAO/PATH/EVB/SP/SQL` con SHA-256 completo (innecesario: 0 colisiones medidas, rompería compatibilidad sin beneficio); tratar `PAR/CALL/UNRES` como identidad con alias post-colisión (oculta el problema en vez de declararlo); inventar un `PROJECT-%03d` o similar posicional para `Project` (ya descartado en R2: no es estable, es artefacto de un renderer legacy congelado).

**Compatibility:** total para los 7 kinds preservados. Aditiva para los 4 kinds con ID V5 nuevo (no existían como entidad direccionable antes). `legacy_ref` es un campo nuevo opcional, no rompe nada.

**Migration:** ninguna en datos V4.3. V5.1 implementa el detector de colisiones y la asignación de IDs V5 nuevos al construir `evidence/`.

**Acceptance test:** `id_unique_per_kind` se exige solo sobre `{EP, EVB, FLOW, DAO, SP, SQL, PATH, PRJ, CMP, XDP, CAL, UnresolvedBoundary}`; `PAR/CALL/UNRES` quedan excluidos de esa invariante y se validan solo como `legacy_ref` no ambiguo cuando sea posible. `entry_point_to_flow_cardinality` valida `0..1`, no `1`.

**Deferred:** si el criterio de "duplicate ordinal determinista" de `Call` necesita refinarse a escala completa de IST (más allá de la muestra medida en R2), es trabajo de V5.1, no de esta ronda.

### DR-R2-02 — Completar Normalized Evidence (APROBADO)

**Problem:** R1 dejaba 12 grupos de campos de `index/*.json` sin destino en la tabla de entidades (criterio "todo campo V4.3 tiene destino" incumplido).

**Decision:** se extiende el contrato con las entidades/relaciones/vistas listadas en NORMALIZED EVIDENCE COMPLETION más abajo, clasificando cada grupo como `core entity`, `core relation`, `adapter extension`, `derived projection` o `legacy-only field`, sin duplicar como evidencia canónica nada derivable de forma exacta, y preservando el orden legacy donde D-01 lo exige.

**Rationale:** ningún dato de V4.3 es irrecuperable (confirmado en R2); completar la tabla es aditivo y no exige tocar ninguna D-xx existente, solo ampliarlas.

**Alternatives rejected:** dejar los 12 grupos fuera del core y remitirlos solo a `extensions` (pierde su carácter de evidencia primaria neutral para los que no son específicos de tecnología, p. ej. `Method`, `FlowGraph`, `Instantiation`); tratarlos todos como `derived projection` (falso para los que son evidencia primaria sin la cual `evidence/` perdería información, p. ej. `Solution`, `ConfigurationEntry`).

**Compatibility:** aditiva; no cambia ningún campo ni ruta V4.3 existente.

**Migration:** V5.1 construye estas entidades/vistas junto con las ya contratadas en R1.

**Acceptance test:** `all_v4_3_fields_have_destination` (cobertura de campos de `index/*.json` en núcleo, `extensions` o `derived projection`, sin campos huérfanos).

**Deferred:** el schema físico exacto (nombres de propiedad, particiones) se fija en V5.1 con medición, igual que D-03 ya difería el formato físico.

### DR-R2-03 — Observabilidad por sidecar (APROBADO)

**Problem:** D-12 de R1 proponía observabilidad dentro de `RUN_SUMMARY.json`, pero R2 demostró que rompe 3 tests vigentes: igualdad exacta del conjunto de claves, byte-identidad entre runs equivalentes, y ausencia de timestamps.

**Decision:** `D-12` se corrige. `RUN_SUMMARY.json` permanece byte/deterministic-compatible con V4.3, sin campos nuevos y sin timestamps. `RUN_OBSERVABILITY.json` se introduce como sidecar aditivo, no determinista, explícitamente fuera de D-01. Contenido y clasificación en OBSERVABILITY SIDECAR CONTRACT más abajo.

**Rationale:** ningún lector de producción lee `RUN_SUMMARY.json` (confirmado en R2: solo se escribe y se hashea); los únicos lectores reales son 3 tests que exigen exactamente el contrato V4.3. Mover la observabilidad a un archivo propio preserva D-01 sin sacrificar la información operativa que V5 necesita.

**Alternatives rejected:** relajar los 3 tests para admitir `observability` en `RUN_SUMMARY.json` (exige tocar tests, prohibido en esta ronda y en general contradice el principio de compatibilidad V4.3 de D-01); omitir observabilidad hasta V5.3 (pierde valor diagnóstico temprano sin necesidad, dado que el sidecar es aditivo y no arriesga nada).

**Compatibility:** total; `RUN_SUMMARY.json` no cambia. `RUN_OBSERVABILITY.json` es un archivo nuevo; los lectores V4.3 lo ignoran porque no lo conocen.

**Migration:** ninguna; V5.1 empieza a emitir el sidecar junto con `RUN_SUMMARY.json`.

**Acceptance test:** los 3 tests de R2 (conjunto exacto de claves, determinismo entre runs, ausencia de timestamps) siguen pasando sin modificación sobre `RUN_SUMMARY.json`; `RUN_OBSERVABILITY.json` puede faltar sin que ningún test de evidencia falle.

**Deferred:** el formato exacto (JSON plano vs por-stage anidado) puede refinarse en V5.1; la clasificación `required/optional/diagnostic` de esta ronda es el contrato mínimo.

### DR-R2-04 — EvidenceReference (APROBADO)

**Problem:** la fila `EvidenceReference` de R1 era contradictoria (identidad "estructural" `{source_id, kind, locator}` vs. obligatorios `entity_id, entity_kind`) y no cubría las 4 formas reales de referencia presentes en V4.3, además de prometer una columna (`source_span`) que V4.3 nunca tuvo.

**Decision:** se reemplaza por una unión etiquetada `ref_type`, con los 4 tipos mínimos y reglas definidas en EVIDENCE REFERENCE CONTRACT más abajo (`entity`, `source`, `source_span` reservado, `textual`), más un campo opcional `legacy_ref` para preservar `CALL-`/`PAR-`/`UNRES-` u otra referencia legacy no única.

**Rationale:** V4.3 tiene evidencia real de las 4 formas (ID de entidad resoluble; ubicación de fuente + fragmento con solo línea, sin columna; entidad completa embebida como objeto; texto técnico no-ID); una única forma de referencia no puede representarlas sin perder información o inventar datos (columna) que no existen.

**Alternatives rejected:** mantener una sola forma estructural forzando todo a `{entity_kind, entity_id}` (pierde las referencias textuales y de ubicación real); inventar columnas para V4.3 (fabrica evidencia inexistente, viola "no fabricar relaciones" de `AGENTS.md`).

**Compatibility:** aditiva; ninguna referencia V4.3 pierde información al mapearse a alguno de los 4 tipos + `legacy_ref`.

**Migration:** ninguna en datos; V5.1 usa la unión al construir `provenance`/`promotion_basis`.

**Acceptance test:** `evidence_reference_resolves_or_fails_explicitly` — toda referencia se clasifica en un `ref_type` válido; una referencia rota se detecta explícitamente, nunca se ignora en silencio.

**Deferred:** `source_span` con columnas reales queda reservado hasta que exista un extractor que las produzca (no antes de V5.4, ver Adapter Contract de R1).

## D-01..D-16 AMENDMENT MATRIX

| D | Estado tras R2A | Nota |
|---|---|---|
| D-01 | unchanged | Confirmado `VIABLE_WITH_CONSTRAINTS` por R2; sin cambios en R2A. |
| D-02 | **amended (D-02 Amendment R2A)** | Ver DR-R2-01. `EP/EVB/FLOW/DAO/SP/SQL/PATH` = identidad V5; `PAR/CALL/UNRES` = `legacy_ref`; `Project/Component/ExternalDependency/Call/UnresolvedBoundary` reciben IDs V5 nuevos; `id_unique_per_kind` se acota a los kinds con identidad real. |
| D-03 | unchanged | Persistencia particionada sin cambios; su constraint (cubrir entidades DR-R2-02) queda satisfecha por la ampliación de este documento. |
| D-04 | unchanged | Round-trip `evidence/ → index/` sigue viable; ahora completable de extremo a extremo gracias a DR-R2-02. |
| D-05 | unchanged | Sin conflicto. |
| D-06 | unchanged | `state`/`promotion_basis` sin cambios de fondo; `promotion_basis` ahora tipado explícitamente vía DR-R2-04. |
| D-07 | unchanged | `template_truth_invariance` sigue siendo el contrato; su verificabilidad mejora con DR-R2-01/04 (refs `CALL-`/`UNRES-` dejan de tratarse como identidad ambigua). |
| D-08 | unchanged | Sin conflicto (`VALIDATED` en R2). |
| D-09 | unchanged | Sin conflicto nuevo. |
| D-10 | unchanged | Matriz de brechas de provider sin cambios; ninguna brecha toca evidence/selection. |
| D-11 | unchanged | Sin conflicto nuevo. |
| D-12 | **amended (D-12 Amendment R2A)** | Ver DR-R2-03. Observabilidad sale de `RUN_SUMMARY.json`; se introduce `RUN_OBSERVABILITY.json` como sidecar aditivo fuera de D-01. |
| D-13 | unchanged | Ver TEST BASELINE DECISION: se fija la decisión, sin tocar tests. |
| D-14 | unchanged | Campos de cache siguen cabiendo sin breaking change; sin relación directa con los 4 conflictos de R2A. |
| D-15 | unchanged | Campos de segmentación sin cambios; invariantes `included ∩ omitted = ∅` ya recomendadas por R2 quedan confirmadas, sin requerir nuevo Decision Record. |
| D-16 | unchanged | Frontera Evidence → Proposal → Decision → Canonical sin cambios; DR-R2-04 refuerza que las proposals exigen refs `entity`, consistente con D-16 tal como estaba. |

Ampliaciones asociadas registradas (sin renumerar): el contenido de `D-03/D-04` (persistencia y proyección de `index/`), `D-06` (unión `EvidenceReference` en `promotion_basis`/`provenance`), `D-07` (verificabilidad de `template_truth_invariance`), `D-14`/`D-15` (compatibilidad de cache y segmentación con las nuevas identidades) quedan ampliadas por referencia cruzada a DR-R2-01…04, sin que su texto original en R1 se contradiga.

## IDENTITY CONTRACT CORRECTIONS

Resumen ejecutable de DR-R2-01, como corrección directa a la tabla "Entidades" de R1:

| Entidad | Identidad V5 (corregida) | Fuente V4.3 | Colisiones medidas | Clave natural |
|---|---|---|---|---|
| `EntryPoint` | `EP-` (preservado) | `entry_points.json` | 0/12 662 | — (ID ya persistido) |
| `EventBinding` | `EVB-` (preservado) | `event_bindings.json` | 0/12 662 | — |
| `FunctionalFlow` | `FLOW-` (preservado) | `functional_flows.json` | 0/12 642 | — |
| `DataOperation` | `DAO-` (preservado) | `data_access.json` | 0/20 082 | — |
| `DataObject` (stored procedure) | `SP-` (preservado) | `stored_procedures.json` | 0/5 389 | — |
| `DataObject` (sql operation) | `SQL-` (preservado) | `sql_operations.json` | 0/3 | — |
| `FunctionalPath` | `PATH-` (preservado, SHA-256 ya) | `functional_paths.json` | 0/170 020 | — |
| `Project` | `PRJ-` (**nuevo**, SHA-256 completo) | sin ID en `projects.json` | n/a (nunca existió) | path normalizado |
| `Component` | `CMP-` (**nuevo**, SHA-256 completo) | sin ID en `symbols.json`/`webforms.json` | n/a | kind + source artifact + name + discriminador determinista |
| `ExternalDependency` | `XDP-` (**nuevo**, SHA-256 completo) | sin ID en `dependencies.json`/aristas embebidas | n/a | tipo + source + target + metadata mínima estable |
| `Call` | `CAL-` (**nuevo**, SHA-256 completo) | `CALL-` transitorio, no persistido | 27 colisiones + 1 383 duplicados de tupla (referencia, no aplica al ID nuevo) | source artifact + containing symbol + line + expression + duplicate ordinal determinista |
| `UnresolvedBoundary` | derivado estable de `path_id` (**nuevo esquema**, no `UNRES-`) | `flow_unresolved` (vista filtrada de paths) | `UNRES-`: 25 colisiones (descartado como identidad) | `path_id` + boundary type/target cuando sea necesario |
| `DataParameter` | sin identidad canónica V5; `PAR-` → `legacy_ref` | `data_parameters.json` | 5/74 633 | entidad hija de `DataOperation`, indexada por posición determinista, no por `PAR-` |

Regla general: ningún ordinal de desambiguación se basa en orden de iteración no determinista (p. ej. orden de un `dict`/`set` en memoria); todo ordinal deriva de una clave estable ya presente en la evidencia (posición en la lista tal como la emite el extractor por artefacto, o el propio contenido de la tupla).

`EntryPoint → FunctionalFlow`: `1:0..1` (corregido desde `1:1`).

## NORMALIZED EVIDENCE COMPLETION

Clasificación de los 12 grupos de campos sin destino identificados por R2 (`ROUND-TRIP FIELD MAPPING`), resolviendo DR-R2-02:

| Grupo V4.3 | Clasificación | Destino |
|---|---|---|
| `solutions` (`.sln`, 113) | **adapter extension** + **core relation** | `Project.member_of` (relación mínima de agrupación en el core, neutral); el resto del `.sln` (type_guid, guid) en `extensions["vbnet-webforms-oracle"]`. |
| `logical_symbols` (1) | **core entity** | `Component` con variante lógica/partial: `partial: bool`, `parts[]` (referencias a los `Component` físicos que lo componen). |
| `entry_points.outgoing_calls[]` (8 481) | **core relation** | `Call` con `owner_entry_point_id` opcional cuando la llamada nace directamente de un handler de `EntryPoint` en vez de un `Method`. |
| `event_bindings` (`EVB-`, 12 662) | **core entity** | `EventBinding` de primera clase (D-02: identidad preservada); comparte referencia a `EntryPoint`/`Component`, no se fusiona con él. |
| `calls.instantiations[]` (40 278) | **core entity** | `Instantiation` (nueva): `type_name`, `variable_name`, `containing_symbol_ref`, `resolved_type_ref?`, origen de la relación `InstantiatesClass`. |
| `calls.imports[]` (9 113) | **adapter extension** | `Import` (VB `Imports`) namespaced en `extensions[adapter_id]` de `Component`/`SourceArtifact`; no es un concepto neutral fuera de VB.NET. |
| `stored_procedures` (`SP-`, 5 389) / `sql_operations` (`SQL-`, 3) | **core entity** | `DataObject` (nueva; identidad `SP-`/`SQL-` preservada, D-02) como nodo terminal de `FunctionalPath`, referenciado desde `DataOperation`. |
| `data_parameters` (`PAR-`, 74 633) | **core entity** (sin identidad canónica propia) | `DataParameter`, entidad hija de `DataOperation.parameters[]`; `PAR-` viaja como `legacy_ref` (DR-R2-01/04), no como `id`. |
| `functional_flows.nodes[]`/`edges[]`/`terminal_operations[]` | **core entity** (`FlowGraph`) | `FlowGraph` embebido en `FunctionalFlow`: `nodes[]`, `edges[]` (con `relation_types`/`evidence_refs`), `terminal_operations[]`. No derivable solo de `FunctionalPath` (confirmado por R2). |
| `dependencies` (26 961 aristas) | **derived projection** | Vista derivada de `Project.dependencies[]` / `ExternalDependency`; se persiste con su orden propio (no es recomputable en orden idéntico solo desde las entidades, según hallazgo de R2). |
| `functional_dependencies` (335 698) | **derived projection** | Vista derivada de `Call`/`Instantiation`/`DataOperation`; orden propio a fijar en V5.1, no evidencia primaria adicional. |
| `configuration` (60, `appSettings`/`connectionStrings`/…) | **adapter extension** | Todo bajo `extensions["vbnet-webforms-oracle"]` de `SourceArtifact`/`Project`; sin excepción, es específico de `.config`/ASP.NET. |
| `repository` (root/stats/ignored/duration_seconds) | **derived projection** + **legacy-only field** | `stats`/`ignored` → resumen de `ScanSummary` (nueva, derivada de `EVIDENCE_MANIFEST.source_snapshot`); `duration_seconds` → **legacy-only field**, fuera de `evidence/`, solo en la proyección `repository.json` (ya excluido de D-01). |

Entidades/vistas nuevas incorporadas formalmente al NORMALIZED EVIDENCE CONTRACT de R1 (sección "Entidades"): `Solution` (agrupación mínima), `Method`/`MethodReference` (referencia de nodo en `FunctionalPath.nodes[]`, hoy texto sin ID — pasa a referencia tipada `component_id` + `method_name` o `MethodReference` estructurado), `FlowGraph` (embebido en `FunctionalFlow`), `DataObject`, `DataParameter`, `Instantiation`, `Import` (extension), `EventBinding`, `ConfigurationEntry` (extension), `ScanSummary`.

Vistas/relaciones incorporadas como `derived projection`: `dependencies`, `functional_dependencies`, `flow_unresolved` (ya contratada en R1 como vista filtrada de `FunctionalPath`, confirmada), `flow_summary` (ya contratada en R1), `logical_symbols` (pasa a `core entity`, no queda como vista), `outgoing_calls` (pasa a `core relation` vía `Call.owner_entry_point_id`).

Regla aplicada de forma consistente: nada se duplica como evidencia canónica si es derivable de forma exacta desde otra evidencia ya persistida (`flow_unresolved`, `flow_summary`, `dependencies`, `functional_dependencies` permanecen `derived projection`); el orden legacy de cada proyección derivada se persiste explícitamente cuando R2 demostró que no es recomputable por una clave simple (caso `dependencies`, `flow_unresolved`).

## OBSERVABILITY SIDECAR CONTRACT

`RUN_SUMMARY.json`: sin cambios respecto a V4.3. No incorpora `observability`, timestamps, ni ninguna clave nueva. Sigue siendo byte-determinista y participando en D-01.

`RUN_OBSERVABILITY.json`: archivo sidecar nuevo, aditivo, generado junto a `RUN_SUMMARY.json` pero **fuera** de D-01 (no participa en comparaciones byte-deterministas ni en `legacy_projection_byte_equivalence`).

| Campo | Clase |
|---|---|
| `stage_started_at` | required |
| `stage_finished_at` | required |
| `duration_ms` | required |
| `input_count` | required |
| `output_count` | required |
| `cache_hit` | optional (presente desde V5.3; `null` antes) |
| `cache_miss` | optional (presente desde V5.3; `null` antes) |
| `provider_calls` | optional (solo stages con IA) |
| `payload_estimated_tokens` | optional (solo stages con IA) |
| `peak_memory_mb` | diagnostic (best-effort, `null` si no medible en la plataforma) |
| `threads_alive_at_exit` | diagnostic (solo si se investiga el riesgo `PROCESS EXIT` de R1) |

Reglas del sidecar (heredadas de D-12 original de R1, sin cambios de fondo, solo de ubicación):

- No es evidence: no forma parte de `evidence/`, no tiene `state`, no tiene `provenance`.
- No participa en byte-equivalence (D-01 no lo cubre).
- Puede faltar sin invalidar ninguna evidencia ni proyección: su ausencia no es un error de validación.
- No altera exit codes (`0/1/2/4` siguen determinados solo por el resultado del pipeline, nunca por la presencia/ausencia del sidecar).
- No contiene secretos ni contenido de fuente (mismo sanitizador central que el resto de outputs).

## EVIDENCE REFERENCE CONTRACT

`EvidenceReference` se define como unión etiquetada por `ref_type`, reemplazando la fila contradictoria de R1:

**`entity`**
```text
{
  ref_type: "entity",
  entity_kind,
  entity_id
}
```
Cubre referencias a cualquier entidad del core (`FLOW-`, `PATH-`, `EP-`, `DAO-`, `SP-`, `SQL-`, `PRJ-`, `CMP-`, `XDP-`, `CAL-`, identidad de `UnresolvedBoundary`, etc.).

**`source`**
```text
{
  ref_type: "source",
  source_id,
  line?,
  excerpt?
}
```
Cubre el patrón real de V4.3 `{file, line, expression}` en `evidence[]` de `EP/EVB/DAO/PAR/SP/SQL` (solo línea, nunca columna en V4.3).

**`source_span`** (reservado, no requerido para V4.3)
```text
{
  ref_type: "source_span",
  source_id,
  start_line?,
  start_column?,
  end_line?,
  end_column?
}
```
No se fabrican columnas para V4.3: este tipo queda reservado hasta que un extractor futuro (V5.4+) las produzca realmente.

**`textual`**
```text
{
  ref_type: "textual",
  text,
  origin?
}
```
Cubre referencias no-ID reales como `dependencies.evidence` (`"InitializeComponent()"`), `functional_dependencies.evidence`/`evidence_samples`, y `symbols/logical_symbols.evidence` (`"Partial declarations"`).

**`legacy_ref`** (campo opcional, no un `ref_type` propio)
Preserva `CALL-`, `PAR-`, `UNRES-` u otra referencia legacy no única (DR-R2-01), disponible junto a cualquiera de los 4 tipos anteriores cuando aplique.

Reglas:

- `promotion_basis` y `provenance` usan esta unión, no una forma única.
- Las proposals deben usar refs `entity` para grounding canónico (consistente con D-16); los subtipos `source`/`source_span`/`textual` no sirven como base de una proposal.
- Las referencias legacy ambiguas (`CALL-`/`UNRES-` con colisión) pueden conservarse vía `legacy_ref` pero nunca cuentan como identidad única ni como `ref_type: "entity"`.
- Una referencia rota (`entity_id` que no resuelve en el store, `source_id` inexistente) debe detectarse explícitamente por el validador — nunca ignorarse en silencio ni tratarse como éxito parcial.

## TEST BASELINE DECISION

Se acepta formalmente la recomendación de R2: **Opción A**.

Decisión contractual (fija el criterio; no modifica ningún test):

1. `PROJECT_STATE.json` representa el estado/historia acumulada del proyecto y puede avanzar legítimamente entre rondas; no es un snapshot congelado de una fase concreta.
2. Las invariantes históricas de una fase (p. ej. "V4 tuvo 0 llamadas reales a IA") pertenecen a los artefactos congelados de esa fase, no a `PROJECT_STATE.json` vivo. Para V4 ese artefacto es `output/v4_r14/V4_FINAL_BASELINE.json`, cuyo test (`test_provider_and_llm_calls_zero`) ya pasa hoy y sigue pasando sin cambios.
3. Las aserciones `provider_calls == 0` / `real_llm_calls == 0` de `tests/test_v4_r13_regression_and_security.py` (`:740`) y `tests/test_v4_r14_manuals_and_final_baseline.py` (`:89`, `:510`) deben dejar de evaluarse contra `PROJECT_STATE.json` vivo; esa afirmación histórica ya está cubierta por el artefacto congelado del punto 2.
4. `test_baseline_matches_on_disk_artifact` (`tests/test_v4_r14_manuals_and_final_baseline.py:334`) debe normalizar también los campos `provider_calls` y `real_llm_calls` cuando compare el baseline reconstruido contra el `PROJECT_STATE.json` vivo, siguiendo el mismo patrón `REG-002` que ya aplica a otros campos que avanzan legítimamente (p. ej. `test_count`).

**IMPORTANTE:** R2A no modifica ningún test. Esta sección fija únicamente la decisión aprobada; la corrección física de los 4 tests (`tests/test_v4_r13_regression_and_security.py:740`, `tests/test_v4_r14_manuals_and_final_baseline.py:89,510,334`) debe ejecutarse en una ronda posterior, autorizada explícitamente, con `PROJECT_STATE.json` sin editar retroactivamente. Hasta esa ronda, el baseline V5 sigue siendo: 2169 tests totales (cifra de R1, no reejecutada en R2A), 4 fallos conocidos y clasificados, 132 skips esperados.

## UPDATED ACCEPTANCE CRITERIA FOR R3

R3 debe poder demostrar, con evidencia, que:

1. DR-R2-01, DR-R2-02, DR-R2-03 y DR-R2-04 quedaron incorporados literalmente al contrato consolidado (sin reabrir su texto salvo con un nuevo Decision Record).
2. No quedan identidades V4.3 inventadas: `Project`, `Component`, `ExternalDependency`, `Call`, `UnresolvedBoundary` usan exclusivamente los esquemas de identidad V5 definidos en IDENTITY CONTRACT CORRECTIONS (`PRJ-`, `CMP-`, `XDP-`, `CAL-`, identidad derivada de `path_id`), nunca un "ID V4.3" que no existe.
3. `PAR-`, `CALL-`, `UNRES-` no se usan como identity key V5 en ningún contrato, invariante o test nuevo; solo aparecen como `legacy_ref`.
4. Todos los campos de V4.3 (`index/*.json`) tienen destino explícito: core entity, core relation, adapter extension, derived projection o legacy-only field — sin grupos huérfanos (los 12 grupos de DR-R2-02 quedan cerrados).
5. `EvidenceReference` ya no es ambigua: toda referencia real de V4.3 se clasifica en uno de los 4 `ref_type` (o `legacy_ref`), sin contradicción entre identidad estructural y campos obligatorios.
6. La observabilidad quedó fuera de `RUN_SUMMARY.json`: los 3 tests que R2 identificó como lectores reales (conjunto exacto de claves, determinismo entre runs, ausencia de timestamps) siguen intactos y pasando sin modificación; `RUN_OBSERVABILITY.json` es el único vehículo de las métricas nuevas.
7. La Opción A de TEST BASELINE DECISION quedó fijada como decisión contractual aprobada, previa a cualquier corrección física de tests.
8. No existe conflicto restante entre D-01…D-16 (la D-01..D-16 AMENDMENT MATRIX de este documento no deja ningún `CONTRACT_CONFLICT` abierto).
9. V5.1 puede empezar sin redefinir el modelo normalizado: el contrato consolidado (R1 + correcciones de R2A) es suficiente para construir `evidence/` sin nuevas decisiones de identidad, cobertura de campos, observabilidad o referencias.

## RISKS

1. El "duplicate ordinal determinista" de `Call` (`CAL-`) no se verificó a escala completa de IST en esta ronda (documental); si el criterio elegido en V5.1 no es realmente determinista entre re-ejecuciones, `id_unique_per_kind` podría fallar de forma nueva. Mitigación: V5.1 debe correr el detector de colisiones también sobre `CAL-` antes de cerrar V5.1.
2. `Component` tiene un duplicado real conocido `(file, name, kind)` (`cc\cc\ccTMP.vb`/`ccRma1`); el discriminador determinista descrito en DR-R2-01 no se implementó ni probó en esta ronda, solo se especificó. Mitigación: acceptance test dedicado en V5.1.
3. El orden propio de `dependencies`/`functional_dependencies` como `derived projection` (no recomputable por una clave simple, según R2) exige persistir explícitamente su orden de emisión; si V5.1 lo omite, D-01 podría romperse para esos dos índices. Mitigación: incluido explícitamente en NORMALIZED EVIDENCE COMPLETION.
4. `RUN_OBSERVABILITY.json` al no participar en D-01 podría divergir de forma no controlada entre runs equivalentes si no se acota su propio contrato de estabilidad (más allá de "no determinista"); esto es aceptado a propósito por DR-R2-03, pero conviene que V5.1 documente qué campos sí deben ser reproducibles al menos en forma (aunque no en valor).
5. Las referencias `CALL-`/`UNRES-` ambiguas (18 + 396, según R2) siguen sin resolverse individualmente; DR-R2-01/04 las clasifica correctamente como `legacy_ref` no único, pero no elimina la ambigüedad subyacente en los datos legacy. Es un riesgo aceptado, no un defecto de este contrato.
6. Riesgos ya heredados de R1/R2 sin cambios: colisión residual de IDs poly33 fuera de los kinds medidos, tamaño de `evidence/`, `technical_documentation_renderer.py`, contaminación de vocabulario, riesgo intermitente `test_deterministic_run_then_ai_enabled_rerun_same_output`, `PROCESS EXIT` (`NOT_REPRODUCED`).

## DEFERRED ITEMS

- Corrección física de los 4 tests rojos (Opción A) → ronda posterior, autorizada explícitamente, `PROJECT_STATE.json` sin editar retroactivamente.
- Implementación real del detector `id_unique_per_kind` sobre `CAL-`/`CMP-` a escala completa de IST → V5.1.
- Formato físico exacto de `evidence/` (JSONL vs JSON particionado), ya diferido desde R1/R2 → V5.1 con medición.
- `source_span` con columnas reales → no antes de V5.4 (depende de un extractor nuevo).
- Esquema físico de `RUN_OBSERVABILITY.json` (JSON plano vs anidado por stage) → V5.1.
- Creación de `docs/V5/V5_0_R3_...` u otro prompt de ronda siguiente → requiere aprobación humana explícita; no se crea en esta ronda.

## FILES READ

`CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`, `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md`, `docs/V5/V5_0_R2_CONTRACT_VALIDATION.md`, `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`, `prompts/V5_0/V5_0_R2A_CONTRACT_CORRECTIONS_PROMPT.md`.

## FILES MODIFIED

- Creado: `docs/V5/V5_0_R2A_CONTRACT_CORRECTIONS.md`.
- Ningún otro archivo del repositorio modificado.
