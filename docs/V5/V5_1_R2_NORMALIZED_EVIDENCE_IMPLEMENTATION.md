# V5.1 R2 — Normalized Evidence Core: Implementation

## STATUS

`V5_1_R2_IMPLEMENTATION_READY`

Convierte en implementación real el contrato de `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`. No se modificó el roadmap, `PROJECT_STATE.json`, documentación histórica V4.3, ni contratos V5.2/V5.5. No se ejecutó IA real. Ningún resolver/extractor existente fue reescrito (D-04: envolver, no reescribir) — se verificó con evidencia antes de escribir código, no se asumió que la estructura actual coincidiera con el contrato. Sin commits/push/branch (gestión de Git manual del usuario, sin tocar).

## RESUMEN — respuestas directas a las 12 preguntas del criterio de cierre (SS21)

1. **¿El contrato V5.1 de R1 quedó implementado?** Sí, las 19 entidades/conceptos con su clasificación (`CORE_ENTITY`/`CORE_RELATION`/`ADAPTER_EXTENSION`/`DERIVED_PROJECTION`/`LEGACY_ONLY`), identidad, `EvidenceReference`, `evidence/`↔`index/`, e invariantes.
2. **¿Las 5 decisiones abiertas quedaron resueltas con evidencia?** Sí, las 5 (SS1 abajo), cada una con medición real sobre IST, no por intuición.
3. **¿Las identidades son deterministas?** Sí — probado con `id_unique_per_kind` sobre los ~460 000 registros reales que la implementación identifica de nuevo (`PRJ`/`CMP`/`XDP`/`CAL`/`UnresolvedBoundary`/`SRC`/`SOL`): **0 colisiones en los 7**, medido dos veces (con y sin persistencia extendida).
4. **¿`CAL-*` mantiene estabilidad frente a inserciones no relacionadas?** Sí — corregido exactamente como pide la ronda (agrupación por tuple base, no contador global) y probado con el ejemplo literal del prompt (`A,B,B` vs `X,A,B,B`).
5. **¿Las cardinalidades quedaron inequívocamente implementadas?** Sí — medidas y expresadas sin ambigüedad (SS5 abajo, con datos reales, no solo notación).
6. **¿Las 11 invariantes están verificadas?** Sí, las 11 implementadas en `legacy_documenter/evidence/invariants.py` y ejercitadas por tests; ninguna sustituida por una aproximación.
7. **¿La trazabilidad está preservada?** Sí — `EvidenceReference`/`resolve_against` con fallo explícito ante referencia rota; probado (`TraceabilityTests`).
8. **¿`UnresolvedBoundary` mantiene correctamente la semántica unresolved?** Sí — `state` fijo por diseño (`__post_init__` rechaza cualquier otro valor), y el conteo de boundaries generados coincide exactamente con `flow_unresolved.json` (162 914/162 914 en IST real).
9. **¿La proyección legacy continúa funcionando?** Sí — los 22 índices se reconstruyen byte a byte tanto sobre el fixture de test como sobre el `index/` real completo de IST (medido, no asumido).
10. **¿La implementación funciona sobre el target real de IST?** Sí — corrida completa sobre `C:\Users\cgalianj\source\IST_40\Operacional` (vía el `index/` ya producido por R0, sin re-escanear): 230 356 `Call`, 162 914 `UnresolvedBoundary`, 15 138 `SourceArtifact` con `sha256` real calculado, 0 colisiones, proyección idéntica.
11. **¿La suite completa continúa pasando?** Sí — 2214 tests, 0 failures, 0 errors, 132 skips, en dos corridas consecutivas.
12. **¿Existe alguna decisión que deba pasar a R3?** Sí — 3 puntos explícitos en RISKS/DEFERRED (el CLI de producción no está todavía cableado a `evidence/`; el formato físico definitivo sigue diferido; y una brecha de cobertura de campos legacy que R1 no midió con precisión suficiente, detallada abajo).

## 1. DECISIONES ABIERTAS DE R1 — RESUELTAS CON EVIDENCIA

### 3.1 Solution identity

**Resuelto:** `SOL-`+SHA-256(path), mismo patrón que `Project`/`PRJ-`. Justificación: `grep` confirmó que ningún consumidor del código actual (`orchestration/`, `context/`, `knowledge/`) lee o espera un campo `id` en `solutions.json`; introducir uno fresco no tiene riesgo de compatibilidad. Medido sobre IST real: 113 soluciones, 0 colisiones.

### 3.2 Method / MethodReference

**Resuelto: sin identidad canónica V5 en esta ronda.** El extractor actual (`_flow_key_labels.method_key`) identifica un método por la tupla `(project, class, method)` sin rastrear firma/sobrecarga — no existe ninguna señal determinista en el código actual para distinguir dos sobrecargas del mismo nombre. La instrucción de esta misma ronda ("No introducir una identidad que el extractor actual no pueda producir de manera determinista") aplica literalmente aquí: inventar un `MTH-` sin esa capacidad de extracción sería fabricar una identidad que el sistema no puede garantizar. `MethodReference` permanece como referencia estructural (`component_id` + texto del método, sin cambios respecto a V4.3) — no se implementó como entidad independiente. Queda documentado para R3/adapters futuros si el extractor llega a rastrear firmas.

### 3.3 Component discriminator

**Resuelto y medido:** discriminador = posición ordinal (0-based) entre registros que comparten exactamente `(file, name, kind)`, asignado en el orden de aparición ya determinista de la lista fuente (`DuplicateOrdinalAssigner`, reutilizado también para `Call`). Medido sobre `symbols.json` real: **6 513 símbolos, 1 solo grupo duplicado** (`cc\cc\ccTMP.vb` / `ccRma1` / `class`, 2 registros) — exactamente el caso que R0/R1 habían identificado. El discriminador separa correctamente los dos registros (`discriminator=0` y `1`), confirmado por test dedicado que reproduce el caso real.

### 3.4 CONN-

**Resuelto:** `CONN-` se convierte en `ExternalDependency(dependency_kind="database_connection")` con identidad `XDP-` nueva, deduplicado por el valor legacy `CONN-` (conservado como `legacy_ref`) — no se inventó una entidad nueva solo para preservar el nombre histórico: se reutilizó `ExternalDependency`, que ya existía en el contrato para el mismo propósito general (dependencia externa de un `Project`/operación). Medido sobre IST real: **12 aristas `DataAccessOperation -> Connection` en `functional_dependencies.json`, 1 solo valor `CONN-` distinto en todo el target** (`CONN-0896442767`, nombre de variable `SqlConnection1`, reutilizado en 2 archivos) — 0 colisiones posibles con un solo valor.

### 3.5 unknown state

**Resuelto: no se introduce.** `grep` exhaustivo de toda asignación de `confidence`/`state` en `analysis/*.py` confirma que el código actual solo produce `"confirmed"`/`"unresolved"` — ningún tercer valor existe en ninguna ruta de código, y R0/R2 ya habían confirmado empíricamente que `"inferred"` no aparece en datos reales de IST. Introducir `unknown` sin que ningún componente pueda producirlo sería exactamente el tipo de campo inventado que la ronda prohíbe. Queda documentado como extensión posible para un adapter futuro no-VB, no como parte del contrato de V5.1.

## 2. CORRECCIÓN OBLIGATORIA: `CAL-*` duplicate ordinal (SS4.1)

Implementado en `legacy_documenter/evidence/identity.py::DuplicateOrdinalAssigner`. El ordinal se calcula **exclusivamente entre registros que comparten el tuple base completo** `(source_artifact, containing_symbol, line, expression, resolved_target)`, nunca contra un contador global de `calls[]`. Verificado exactamente con el ejemplo del prompt:

```text
A, B, B                    -> ordinales [0, 0, 1]  (A=0, B=0, B=1)
X, A, B, B (X insertado)   -> ordinales [0, 0, 1]  (mismos A, B, B)
```

Test: `CallIdentityStabilityTests.test_unrelated_insertion_does_not_change_existing_call_ids` — pasa. Medido también en IST real: 230 356 `Call`, 880 grupos de tupla idéntica (2 263 registros en esos grupos, 1 383 "extra" — coincide exactamente con R0/R2), **0 colisiones de `CAL-`** tras aplicar la corrección.

## 3. CORRECCIÓN DE CARDINALIDADES (SS5)

Medidas sobre `functional_paths.json`/`data_access.json`/`stored_procedures.json` reales (IST, `C:\Users\cgalianj\source\IST_40\Operacional`), no solo expresadas en notación:

| Relación | Cardinalidad inequívoca | Evidencia medida |
|---|---|---|
| `FunctionalPath → DataOperation` | **N FunctionalPath : 1 DataOperation** (cada `FunctionalPath` tiene como máximo 1 `DataOperation` terminal — 0..1 en el lado del path; una misma `DataOperation` puede ser terminal de 0..N paths distintos) | 4 612 paths con terminal `data_operation`, apuntando a solo 1 157 `DataOperation` distintas; una `DataOperation` es terminal de hasta **254 paths** distintos. |
| `FunctionalPath → DataObject` (stored procedure) | **N FunctionalPath : 1 DataObject** (mismo patrón) | 1 121 paths con terminal `stored_procedure`, apuntando a solo 338 `DataObject` distintas; una hasta **63 paths**. |
| `DataOperation → DataObject` (stored procedure) | **N DataOperation : 1 DataObject** (una `DataOperation` referencia a lo sumo 1 SP; un mismo SP puede ser referenciado por 0..N `DataOperation`) | 9 784 registros de `DataOperation` referencian un SP, apuntando a 5 389 `DataObject` (SP) distintos; uno referenciado por hasta **17 `DataOperation`**. |
| `DataOperation → DataParameter` | **1 DataOperation : N DataParameter** (composición; un `DataParameter` no existe fuera de su `DataOperation`) | 74 633 `DataParameter` sobre 20 082 `DataOperation` (media ≈3.7 por operación). |

No se usa la expresión ambigua `0..1 : 1` en ningún punto del código ni de este documento: cada relación de arriba declara explícitamente qué lado es "a lo sumo uno" y qué lado admite "muchos", sustentado con el conteo máximo real medido.

## 4. ARQUITECTURA IMPLEMENTADA

```text
legacy_documenter/evidence/
    __init__.py       -- runtime-independence docstring; ningún import de docs/prompts/tests
    identity.py        -- sha256_id, poly33_id, detect_collisions, DuplicateOrdinalAssigner
    reference.py        -- EvidenceReference (unión etiquetada), resolve_against, BrokenEvidenceReferenceError
    entities.py          -- SourceArtifact, Solution, Component, ExternalDependency, DataObject,
                            UnresolvedBoundary, CallIdentity, ScanSummary
    builder.py            -- NormalizedEvidenceBuilder: envuelve el dict `indexes` (mismo que producen
                            los resolvers actuales) en NormalizedEvidence, sin reanalizar nada
    persistence.py         -- write_evidence(): persiste evidence/*.json + EVIDENCE_MANIFEST.json
                            (vía atomic_write_text, sin mecanismo de escritura nuevo)
    projection.py           -- LegacyIndexProjector: evidence/ -> indexes dict compatible con V4.3
    invariants.py            -- I-1..I-11 como funciones invocables por tests
```

Cadena implementada, exactamente la del contrato:

```text
Legacy Source --(extractors/*.py, sin cambios)--> Technology Adapter (analysis/*.py, sin cambios)
    --(NormalizedEvidenceBuilder.build)--> Normalized Evidence Core
    --(write_evidence)--> Evidence Persistence (evidence/*.json + EVIDENCE_MANIFEST.json)
    --(LegacyIndexProjector.project)--> Legacy Compatibility Projection (index/* equivalente)
```

**Decisión de alcance explícita, no silenciosa (ver RISKS):** esta cadena está implementada y probada como biblioteca + herramienta de validación (`tools/v5_1_r2_real_ist_regression.py`), **no** está todavía cableada dentro de `legacy_documenter/cli/pipeline_stages.py`/`full_pipeline.py` para que `full`/`analyze` la ejecuten automáticamente en producción. Cablearla implicaría un cambio de comportamiento de cada invocación de CLI existente, que excede "implementar el núcleo" y pertenece más naturalmente a una ronda de integración explícita (R3), evitando así también el riesgo de tocar "comportamiento no relacionado" que esta ronda prohíbe expresamente.

## 5. ENTIDADES IMPLEMENTADAS

Todas las 19 del contrato R1, sin añadir ninguna no justificada:

| Entidad | Implementación | Clasificación |
|---|---|---|
| `SourceArtifact` | `entities.SourceArtifact` (nuevo) | `CORE_ENTITY` |
| `Solution` | `entities.Solution` (nuevo) | `CORE_RELATION` + `ADAPTER_EXTENSION` |
| `Project` | dict con `id`+`extensions` (wrapper sobre el modelo actual) | `CORE_ENTITY` |
| `Component` | `entities.Component` (nuevo; fusiona `Symbol`+`WebForm`) | `CORE_ENTITY` + `ADAPTER_EXTENSION` |
| `Method` | sin entidad propia (SS3.2, resuelto) | referencia estructural |
| `MethodReference` | sin entidad propia (SS3.2, resuelto) | referencia estructural |
| `EntryPoint` | passthrough (preservado, sin cambios) | `CORE_ENTITY` |
| `EventBinding` | passthrough (preservado, sin cambios) | `CORE_ENTITY` |
| `Call` | `entities.CallIdentity` (side-table nuevo, no muta `calls.json`) | `CORE_ENTITY` |
| `Instantiation` | passthrough (dentro de `calls.json`, ya existe como dataclass en `models/call.py`) | `CORE_ENTITY` |
| `DataOperation` | passthrough (preservado) | `CORE_ENTITY` |
| `DataObject` | `entities.DataObject` (nuevo, envuelve SP/SQL) | `CORE_ENTITY` |
| `DataParameter` | passthrough (preservado) | `CORE_ENTITY` |
| `ExternalDependency` | `entities.ExternalDependency` (nuevo) | `CORE_ENTITY` |
| `FunctionalPath` | passthrough (preservado) | `CORE_ENTITY` |
| `FunctionalFlow` | passthrough (preservado) | `CORE_ENTITY` |
| `FlowGraph` | passthrough (embebido en `FunctionalFlow`) | `CORE_ENTITY` |
| `UnresolvedBoundary` | `entities.UnresolvedBoundary` (nuevo, derivado de `flow_unresolved`) | `CORE_ENTITY` |
| `EvidenceReference` | `reference.EvidenceReference` (nuevo, unión etiquetada) | estructural |
| `ScanSummary` | `entities.ScanSummary` (nuevo, deriva de `repository.json`) | `DERIVED_PROJECTION` |

## 6. IDENTIDADES

| Prefijo | Estado | Fórmula | Colisiones medidas (IST real) |
|---|---|---|---|
| `EP-`,`EVB-`,`FLOW-`,`DAO-`,`SP-`,`SQL-`,`PATH-` | preservados, sin cambios | las del código V4.3 existente | 0 (heredado, no re-medido en esta ronda: los índices no se tocaron) |
| `PRJ-` | nuevo | `sha256_id("PRJ", path)` | 0/259 |
| `CMP-` | nuevo | `sha256_id("CMP", tipo, source_ref, name, kind, discriminador)` | 0/9 859 |
| `XDP-` | nuevo | `sha256_id("XDP", kind, name, source)` | 0/4 839 |
| `CAL-` | nuevo | `sha256_id("CAL", file, containing_symbol, line, expression, resolved_target, duplicate_ordinal)` | 0/230 356 |
| `UnresolvedBoundary` (sin prefijo legacy) | nuevo | `sha256_id("UNB", path_id, terminal_type, terminal_target)` | 0/162 914 |
| `SRC-` | nuevo | `sha256_id("SRC", path_posix)` | 0/15 138 |
| `SOL-` | nuevo | `sha256_id("SOL", path)` | 0/113 |
| `PAR-`,`CALL-`,`UNRES-` | `legacy_ref` únicamente | fórmula poly33 original, preservada | 5/27/25 (heredado de R0/R2, no re-medido — estos nunca fueron identidad canónica en ningún momento) |

`check_i2_no_legacy_ref_as_identity` confirma programáticamente que ningún `id` de `ExternalDependency`/`Call`/`UnresolvedBoundary` comienza con `PAR-`/`CALL-`/`UNRES-` — probado sobre el fixture y sobre IST real.

## 7. EVIDENCEREFERENCE

Implementado exactamente como R1 lo definió: `entity`/`source`/`source_span`/`textual` + `legacy_ref` opcional (`reference.py`). `__post_init__` rechaza en el momento de construcción cualquier referencia que no tenga los campos mínimos de su `ref_type` — nunca se puede construir una referencia inválida silenciosamente. `resolve_against` levanta `BrokenEvidenceReferenceError` de forma explícita cuando una referencia `entity`/`source` no resuelve contra el store; nunca hay una tercera salida "parcialmente válida". Probado con 9 tests dedicados (`EvidenceReferenceTests`) más el uso real en `TraceabilityTests` sobre datos del fixture.

## 8. PERSISTENCE

`evidence/` implementado y probado en dos capas:

1. **Entidades nuevas** (`source_artifacts`, `solutions`, `projects`, `components`, `external_dependencies`, `data_objects`, `call_identities`, `unresolved_boundaries`, `scan_summary`).
2. **Entidades preservadas** (`entry_points`, `event_bindings`, `functional_flows`, `functional_paths`, `flow_unresolved`, `data_access`, `data_parameters`, `calls`, `dependencies`, `functional_dependencies`, `configuration`, `errors`, `logical_symbols`, `flow_summary`) — añadidas explícitamente durante esta ronda tras notar que la primera versión de `persistence.py` solo escribía las entidades nuevas, dejando `evidence/` incapaz de reconstruir `index/` sin retener en memoria el `indexes` dict original. Con la corrección, `evidence/` es un store standalone completo: `index/` es regenerable a partir de él únicamente, sin volver a ejecutar SCAN/EXTRACTION/resolución (D-03/D-04 cumplidos literalmente, no solo en espíritu).

`EVIDENCE_MANIFEST.json` incluye `evidence_schema_version`, `entity_counts` por partición, y SHA-256 por partición — formato físico: JSON pretty-printed por partición (no JSONL todavía; ver DEFERRED). `index/` **no** se convierte en fuente canónica en ningún punto del código: `LegacyIndexProjector` solo lee de `NormalizedEvidence`, nunca al revés.

## 9. COMPATIBILITY PROJECTION

`LegacyIndexProjector.project()` reconstruye los 22 índices de V4.3 a partir de `NormalizedEvidence`. Verificado en dos escalas:

- **Fixture** (`tests/fixtures/v4_2_r7_full_sample`, vía `analyze_repository` real): los 22 índices, comparados tanto contra el dict `indexes` en memoria como contra los archivos `index/*.json` realmente escritos en disco — idénticos.
- **IST real** (`C:\Users\cgalianj\source\IST_40\Operacional`, usando el `index/` ya producido por R0 en `v5_1_new_target_rebaseline`): los 22 índices, comparados contra los archivos reales en disco — **idénticos byte a byte**, incluyendo `repository.json` (con su `duration_seconds` original preservado, al ser passthrough).

Ningún índice legacy fue alterado para forzar la coincidencia (restricción explícita de la ronda, cumplida: `index/*.json` de `v5_1_new_target_rebaseline` no se tocó).

## 10. TESTS AGREGADOS

`tests/test_v5_1_r2_normalized_evidence_core.py`, 45 tests, organizados exactamente en las categorías pedidas por SS12:

- **Unit tests:** `IdentityPrimitiveTests` (5), `CollisionDetectionTests` (3), `DuplicateOrdinalAssignerTests` (2), `EvidenceReferenceTests` (9), `UnresolvedBoundaryStateTests` (2).
- **Contract tests:** `OpenDecisionResolutionTests` (4, una por decisión resuelta con código verificable — `Method` no tiene test propio porque su resolución es "no crear entidad", verificado por ausencia, no por assertion positiva).
- **Identity tests:** `FixtureBackedIdentityTests` (6, incluyendo el caso real de duplicado de `Component`), `CallIdentityStabilityTests` (2, incluyendo el ejemplo exacto del prompt).
- **Traceability tests:** `TraceabilityTests` (1, resolución real de `Component.source_ref` contra el store de `SourceArtifact`).
- **Unresolved tests:** `UnresolvedSemanticsTests` (3).
- **Determinism tests:** `DeterminismTests` (1, sobre el fixture completo vía pipeline real).
- **Compatibility tests:** `LegacyProjectionCompatibilityTests` (4, incluyendo comparación contra `index/*.json` reales en disco).
- **Segmentación (I-11):** `SegmentationFieldConsistencyTests` (3).
- **Persistencia:** `PersistenceTests` (1).

Se mantiene también `tests/test_v4_1_r0_maintainability_inventory.py` — modificado (no un test nuevo) para reflejar la adición legítima de 8 módulos de producción, siguiendo exactamente el patrón ya establecido por ese archivo desde V4.1-R1 en adelante (cada ronda que añade módulos actualiza sus contadores relativos con un comentario justificativo; ver el propio archivo para el precedente). Se documenta explícitamente aquí porque la restricción SS19 exige justificar cualquier cambio adicional imprescindible: sin esta actualización, la suite completa no pasa, no por un defecto de la implementación sino porque ese archivo es, por diseño, un contador acumulativo del inventario de módulos de producción que cada ronda debe mantener.

## 11. RESULTADOS DE TESTS

```text
python -m unittest tests.test_v5_1_r2_normalized_evidence_core
Ran 45 tests in 1.5s
OK
```

```text
python -m unittest tests.test_v4_1_r0_maintainability_inventory
Ran 22 tests in ~13-15s
OK
```

## 12. RESULTADO DE SUITE COMPLETA

Dos corridas consecutivas tras completar la implementación (incluida la extensión de `persistence.py`):

| Corrida | Tests | Failures | Errors | Skips |
|---|---|---|---|---|
| 1 | 2214 | 0 | 0 | 132 |
| 2 | 2214 | 0 | 0 | 132 |

2214 = 2169 (baseline previo al gate PRE-V5.1) + 45 (tests nuevos de esta ronda). Ningún test preexistente fue debilitado ni convertido en trivial; las únicas modificaciones a tests existentes son los contadores acumulativos de `test_v4_1_r0_maintainability_inventory.py` (SS10 arriba).

## 13. RESULTADO DE REGRESIÓN REAL IST

`tools/v5_1_r2_real_ist_regression.py` (dev tooling, fuera del paquete runtime): carga el `index/*.json` ya producido por R0 sobre `C:\Users\cgalianj\source\IST_40\Operacional` (sin volver a escanear), construye `NormalizedEvidence` calculando `SourceArtifact.sha256` sobre los 15 138 archivos reales, proyecta de vuelta, y persiste `evidence/` completo.

```text
Entity counts:
  source_artifacts:        15 138  (sha256 calculado para 15 138/15 138)
  solutions:                  113
  projects:                   259
  components:                9 859  (6 513 symbols + 3 346 webforms)
  external_dependencies:      4 839  (4 838 assembly refs + 1 database_connection)
  data_objects:                5 392  (5 389 SP + 3 SQL)
  call_identities:            230 356
  unresolved_boundaries:      162 914

Collisions (I-1):  PRJ=0  CMP=0  XDP=0  CAL=0  UnresolvedBoundary=0  SRC=0  SOL=0
Projection (I-9):  22/22 índices byte-idénticos al index/*.json real en disco
Determinism (I-10): dos builds sobre el mismo indexes -> evidencia normalizada idéntica byte a byte (197 MB serializados, sin recomputar sha256 de archivo)
Build time: ~27 s (con hashing de contenido real de 15 138 archivos) / ~8 s (sin hashing, x2 builds)
evidence/ total: 1 211 178 539 bytes (≈1.16 GB) -- 8 particiones nuevas + 14 particiones preservadas
```

## 14. COMPARACIÓN CONTRA R0

| Métrica | R0 (`V5_1_R0_NEW_TARGET_REBASELINE.md`) | R2 (esta ronda, mismo target) | Coincide |
|---|---|---|---|
| `entry_points` | 12 662 | 12 662 (passthrough, sin cambios) | ✅ |
| `functional_flows` | 12 642 | 12 642 (passthrough) | ✅ |
| `functional_paths` | 170 020 | 170 020 (passthrough) | ✅ |
| `data_access` | 20 082 | 20 082 (passthrough) | ✅ |
| `data_parameters` | 74 633 | 74 633 (passthrough) | ✅ |
| `stored_procedures` | 5 389 | 5 389 → `data_objects` (envuelto) | ✅ |
| `calls` (archivos) | 4 328 | 4 328 (passthrough); 230 356 `Call` individuales → `call_identities` (nuevo) | ✅ |
| `flow_unresolved` | 162 914 | 162 914 (passthrough); → 162 914 `UnresolvedBoundary` (nuevo, 1:1) | ✅ |
| Colisiones `EP/EVB/FLOW/DAO/SP/SQL/PATH` | 0 (medido en R0) | 0 (heredado, índices sin tocar) | ✅ |
| Colisiones `PAR/CALL/UNRES` | 5/27/25 (medido en R0) | 5/27/25 (heredado, índices sin tocar) | ✅ |
| Colisiones `PRJ/CMP/XDP/CAL/UnresolvedBoundary/SRC/SOL` | no medible (no existían) | **0/0/0/0/0/0/0** (medido por primera vez) | nueva evidencia, sin conflicto |

Ningún conteo diverge de R0. La única información genuinamente nueva es la confirmación de 0 colisiones para las 7 identidades V5 que R0 no podía medir (porque todavía no existían).

## 15. DIFERENCIAS ENCONTRADAS

Ninguna diferencia estructural, semántica o de comportamiento respecto a V4.3/R0. Las únicas "diferencias" son aditivas por diseño:

1. `SourceArtifact.sha256` es información genuinamente nueva (V4.3 nunca la calculó); no reemplaza ni contradice ningún campo existente.
2. `ExternalDependency` materializa como entidad de primera clase algo que V4.3 solo tenía como arista `Dependency` sin identidad propia (CC-1 de R2/R3, ya documentado como brecha a cerrar).
3. `Component` fusiona `Symbol`+`WebForm` conceptualmente, pero la proyección los separa de vuelta en `symbols.json`/`webforms.json` exactamente como antes — no hay pérdida ni fusión observable desde fuera.

## 16. RIESGOS Y DECISIONES PENDIENTES PARA R3

1. **CLI de producción no cableado.** `legacy_documenter/cli/pipeline_stages.py`/`full_pipeline.py` no invocan todavía `NormalizedEvidenceBuilder`/`write_evidence` durante un `full`/`analyze` real — `evidence/` no se genera automáticamente en una corrida de usuario. Esta ronda demuestra el núcleo como biblioteca + herramienta de validación explícita, deliberadamente, para no cambiar el comportamiento observable de cada invocación de CLI existente sin una ronda de integración dedicada. **R3 debe decidir y ejecutar el cableado.**
2. **Formato físico de `evidence/` sigue diferido.** JSON pretty-printed por partición, no JSONL particionado (V5.0/R1 ya lo dejaba como decisión de V5.1 "con medición"; esta ronda no repitió esa medición, priorizando cerrar el núcleo funcional). Tamaño medido (~1.16 GB con passthrough completo) es mayor que la estimación optimista de R2 (0.35–0.85 GB) porque incluye *todas* las particiones preservadas sin deduplicar `flow_unresolved` contra `functional_paths` — **R3 debe decidir si esa deduplicación entra en el formato físico definitivo**.
3. **Brecha de cobertura de `Instantiation`/`Import` como particiones propias.** R1 SS13 notaba que `Instantiation` ya existe como dataclass en `models/call.py` pero nunca se exporta como índice top-level; esta ronda la deja dentro del passthrough de `calls.json` (no se pierde información, pero tampoco se materializó como partición `evidence/instantiations.json` independiente, que sería más fiel al contrato "core entity" de R1). **No es una contradicción del contrato** (la información existe y es trazable), pero es una brecha de fidelidad de modelado que R3 puede cerrar sin romper nada existente.

Ninguno de estos tres puntos es una contradicción del contrato de R1 (no se declara `V5_1_R2_IMPLEMENTATION_CONFLICT`) ni una decisión esencial faltante que bloquee el cierre de esta ronda (no se declara `V5_1_R2_OPEN_DECISION`): son extensiones de alcance explícitamente diferidas, con su razón documentada, tal como exige la restricción de la ronda de no ampliar el alcance sin justificarlo.

## RESTRICCIONES CONFIRMADAS

No se implementaron V5.2/V5.5 (sin provider genérico, templates, profiles, cache, segmentación, approval, plugin runtime). No se modificó el roadmap, `PROJECT_STATE.json`, documentación histórica V4.3, ni contratos V5.2/V5.5. Runtime independence preservada: `legacy_documenter/evidence/*.py` no importa `docs/`, `prompts/`, `tests/`, `PROJECT_STATE.json`, ni `tools/` (verificado por lectura directa de cada import). No se ejecutó IA real, no se creó documentación auxiliar, no se hizo commit/push/branch.

## FILES MODIFIED

- Creado: `legacy_documenter/evidence/__init__.py`, `identity.py`, `reference.py`, `entities.py`, `builder.py`, `persistence.py`, `projection.py`, `invariants.py` (Normalized Evidence Core).
- Creado: `tests/test_v5_1_r2_normalized_evidence_core.py` (45 tests).
- Creado: `tools/v5_1_r2_real_ist_regression.py` (dev tooling; regresión real IST, no forma parte del paquete runtime).
- Modificado: `tests/test_v4_1_r0_maintainability_inventory.py` (mantenimiento imprescindible de sus contadores acumulativos ante los 8 nuevos módulos de producción; justificado en SS10).
- Creado: `docs/V5/V5_1_R2_NORMALIZED_EVIDENCE_IMPLEMENTATION.md` (este documento).
- Generado (fuera del repositorio, en el directorio de resultados de pruebas): `C:\PruebasLegacyMapper\Resultados\v5_1_r2_evidence_build\evidence\` (salida de la regresión real IST) y su `R2_REGRESSION_SUMMARY.json`.
- Ningún otro archivo modificado. `PROJECT_STATE.json` sin tocar (confirmado con `git diff`).
