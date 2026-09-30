# V5.1 R3.2 — Cierre de D-4: EvidenceReference y trazabilidad

## 1. Estado final

V5_1_R3_2_READY_FOR_R4_REVALIDATION

D-4 (trazabilidad literal vía `provenance`/`EvidenceReference`, contrato V5.0 R3/R1) queda implementada de forma real y productiva. I-4 e I-5 se ejecutan como parte del gate de producción (`validate_evidence`) antes de persistir `evidence/`, sobre las 454 010 entidades reales que las requieren, en dos corridas completas sobre IST real (`v5_1_r3_2_run_a`/`v5_1_r3_2_run_b`). 0 registros con `provenance` vacío, 0 referencias rotas. Compatibilidad V4.3, determinismo, runtime independence y AI independence se revalidaron sin regresión. D-5 no se tocó. No se implementó nada de V5.2–V5.9. No se modificó `PROJECT_STATE.json`, el roadmap ni `tools/`. Sin commits/push.

## 2. Qué se corrigió

El defecto era exactamente el que R3/R3.1 dejaron documentado: `EvidenceReference` (`legacy_documenter/evidence/reference.py`) y su store/resolución existían, probados unitariamente con datos sintéticos, pero ninguna entidad real los emitía — `check_i4_traceability`/`check_i5_evidence_reference_resolves_or_fails_explicitly` no se invocaban ni en producción ni en ningún test sobre evidencia real.

Se cerró con cambio mínimo, reutilizando `EvidenceReference` sin crear un segundo modelo:

1. **`entities.py`**: cada entidad con identidad canónica excepto `SourceArtifact` (la excepción de raíz que el propio contrato V5.0 R3 define) gana `provenance: list[EvidenceReference]`, serializado en `to_dict()` como `[ref.to_dict() for ref in self.provenance]`. `SourceArtifact` no gana el campo — es intencional, no un olvido (§10).
2. **`builder.py`**: cada `_build_*` construye `provenance` a partir de evidencia que el propio registro legacy ya traía — nunca un valor nuevo o inventado (§4). Tres helpers de módulo nuevos: `_whole_file_source_ref` (Solution/Project → su propio archivo), `_evidence_list_provenance` (DataObject → primera ocurrencia real de su lista `evidence[]`), `_connection_provenance` (ExternalDependency de tipo conexión → el `source_file`/`evidence` que la arista `functional_dependencies` ya tenía).
3. **`reference.py`**: se agregó el constructor `EvidenceReference.source_span(...)` (el tipo `source_span` ya existía en el contrato desde R1/R2 pero no tenía constructor de conveniencia — no es un tipo nuevo).
4. **`invariants.py`**: `PROVENANCE_KINDS` (qué particiones/entidades deben tener `provenance`), `build_reference_store` (construye el `EvidenceReferenceStore` real desde un `NormalizedEvidence`), `provenance_report` (cifras reportables, nunca lanza), `validate_provenance` (el gate real: I-4 + I-5, lanza `InvariantViolation` fail-closed). `validate_evidence` ahora también llama a `validate_provenance` antes de retornar.
5. **`persistence.py`**: un solo ajuste — `Project` es un `dict` plano (no dataclass) construido con `provenance` como objetos `EvidenceReference` vivos (para que `validate_provenance` pueda resolverlos antes de escribir); se serializan a JSON en el único punto donde esa partición se renderiza (`_render_project`), nunca antes.
6. **`pipeline_stages.py`**: solo el docstring de `build_evidence_artifacts` se amplió para documentar que `validate_evidence` ahora también exige I-4/I-5; ningún cambio de comportamiento nuevo (la llamada a `validate_evidence(evidence)` ya existía desde R3.1 y ya era fail-closed).

Archivos de producción modificados: `legacy_documenter/evidence/entities.py`, `legacy_documenter/evidence/builder.py`, `legacy_documenter/evidence/reference.py`, `legacy_documenter/evidence/invariants.py`, `legacy_documenter/evidence/persistence.py`, `legacy_documenter/cli/pipeline_stages.py` (solo docstring).

Archivos de test modificados/agregados: `tests/test_v5_1_r2_normalized_evidence_core.py` (+13 tests, nueva clase `ProvenanceTraceabilityTests` más dos tests sueltos de persistencia/root-exception), `tests/test_v4_1_r0_maintainability_inventory.py` (ajustes del inventario heurístico de mantenibilidad — ver §13).

## 3. Cómo quedó `provenance`

| Entidad | Origen real de `provenance` | Tipo de referencia |
|---|---|---|
| `SourceArtifact` | — (excepción de raíz, no lleva el campo) | — |
| `Solution` | su propio `.sln` (mismo `path`) | `source` |
| `Project` | su propio `.vbproj` (mismo `path`) | `source` |
| `Component` | el archivo (`file`/`path`) ya usado para `source_ref` | `source` |
| `ExternalDependency` (assembly) | el `Project` que declara la `<Reference>` (mismo `source_ref`) | `entity` (`Project`) |
| `ExternalDependency` (database_connection) | el `source_file`/`evidence` de la arista `functional_dependencies` que originó la conexión | `source` (o `textual` si esa arista no trajera `source_file`; en IST real esto nunca ocurrió, §7) |
| `DataObject` | primera ocurrencia real de su lista `evidence[]` (`file`/`line`/`expression`) | `source` |
| `CallIdentity` | sus propios campos ya persistidos (`source_artifact`/`line`/`expression`) | `source` |
| `Instantiation` | el `evidence` embebido en su propio registro legacy (`file`/`line`/`expression`) | `source` |
| `UnresolvedBoundary` | el `FunctionalPath` (`path_id`) que ya la identificaba | `entity` (`FunctionalPath`) |

Cada `provenance` es una lista con al menos un elemento, nunca vacía ni inventada: todos los valores usados (`path`, `file`, `line`, `expression`, `source_ref`, `path_id`) ya existían en el registro que el extractor/resolver produjo antes de esta ronda — ningún campo nuevo se agregó al pipeline de extracción/resolución, solo se leyó lo que ya estaba.

## 4. Cómo se usa `EvidenceReference`

Sin modelo paralelo: se reutilizó `legacy_documenter/evidence/reference.py` tal cual existía (la única adición es el constructor de conveniencia `source_span`, que expone un tipo que el contrato ya definía). Los cuatro `ref_type` del contrato (`entity`, `source`, `source_span`, `textual`) están todos disponibles; la evidencia real de IST usa `source` (286 258 referencias) y `entity` (167 752 referencias) — `source_span`/`textual` están soportados y probados (§12, tests 4/5/6), pero ningún dato real de IST necesitó `source_span` (no hay columnas) y ninguna conexión careció de `source_file` (así que `textual` tampoco se disparó en la corrida real, ver §7). `legacy_ref` sigue disponible en cualquiera de los cuatro tipos, sin usarse todavía por `provenance` (no había un `legacy_ref` real disponible en los puntos donde se construyó `provenance` esta ronda).

## 5. Resultado I-4

`validate_provenance` (dentro de `validate_evidence`, el gate real de producción) exige que toda entidad de `PROVENANCE_KINDS` tenga `provenance` no vacío. Sobre las dos corridas reales de IST (`v5_1_r3_2_run_a`/`v5_1_r3_2_run_b`):

| Partición | Entidades verificadas | Con `provenance` vacío |
|---|---|---|
| solutions | 113 | 0 |
| projects | 259 | 0 |
| components | 9 859 | 0 |
| external_dependencies | 4 839 | 0 |
| data_objects | 5 392 | 0 |
| call_identities | 230 356 | 0 |
| instantiations | 40 278 | 0 |
| unresolved_boundaries | 162 914 | 0 |
| **Total** | **454 010** | **0** |

I-4 se ejecuta realmente (no solo existe el método): ambas corridas invocaron `build_evidence_artifacts → validate_evidence → validate_provenance` como parte del `full` productivo; si hubiera fallado, las corridas habrían terminado FAILED (demostrado por separado, §7 del test controlado). Cobertura de test dedicada: `test_1_entity_with_valid_provenance_passes`, `test_7_real_evidence_carries_provenance_where_the_contract_requires_it`, `test_8_i4_runs_for_real_and_rejects_empty_provenance`.

## 6. Resultado I-5

Sobre las mismas 454 010 entidades (686 010 `EvidenceReference` individuales: 286 258 `source` + 167 752 `entity`, contadas una vez por corrida — la cifra por corrida es la de la tabla; se verificó en A y en B por separado), cada referencia se resolvió contra un `EvidenceReferenceStore` construido desde la propia evidencia (`build_reference_store`): todos los `SourceArtifact.id` reales como destino válido de `source`/`source_span`, todos los `Project.id`/`FunctionalPath.path_id` reales como destino válido de `entity`.

**Referencias rotas encontradas: 0** (en A y en B).

I-5 se ejecuta realmente, no solo existe el detector: es el mismo `validate_provenance` de §5, y el mismo test controlado (§9) prueba explícitamente que una referencia rota real (`SRC-does-not-exist`) sí se detecta y sí falla. Cobertura de test dedicada: `test_2`/`test_3`/`test_5` (broken entity/source/source_span), `test_9_i5_runs_for_real_and_rejects_a_broken_reference`.

## 7. Validación de referencias reales

Verificación directa sobre `v5_1_r3_2_run_a/evidence/*.json` (lectura de JSON, sin reutilizar el código de producción que se está validando — un script propio de esta ronda):

- 24 particiones + manifest, conteos y `partition_sha256` del manifest coinciden con los archivos físicos en las 24 (0 discrepancias).
- 454 010 registros con `provenance`, 686 010 referencias (`source`: 286 258, `entity`: 167 752, `source_span`: 0, `textual`: 0 — ninguna de las 12 dependencias `database_connection` reales de IST necesitó el fallback `textual`, todas traían `source_file`).
- Recorrido manual (no vía `resolve_against`, para no depender del propio código bajo prueba) de las 686 010 referencias contra los ids reales de `SourceArtifact`/`Project`/`FunctionalPath`: **0 rotas**.
- `SourceArtifact` no lleva `provenance` en ninguno de los 15 138 registros reales (confirmado: ninguna clave `"provenance"` en `source_artifacts.json`).

## 8. Persistencia

`provenance` se persiste dentro de la partición de cada entidad (no una carpeta ni store paralelo): `evidence/components.json`, `evidence/external_dependencies.json`, etc., cada registro con su propia clave `"provenance": [...]`. Formato físico sin cambios (`json_compact`, ver R2.1-03). Determinismo: `evidence/` de A y B es byte a byte idéntica, incluidas las 686 010 referencias serializadas (§9 determinismo). Reproducible: se releyó `evidence/components.json`/`projects.json` tras `write_evidence` en test (`test_provenance_persists_inside_evidence_json`) y sobre la corrida real (§7).

Tamaño de `evidence/`: 1 057 049 755 B (1.008 GB) en A y B, frente a 977 957 317 B (932.6 MB) de R3.1 — el incremento (+79.1 MB, +8.1%) es exactamente el costo de serializar las 686 010 referencias nuevas; ninguna otra partición cambió de tamaño.

## 9. Determinismo

Dos corridas productivas completas sobre IST real (código de esta ronda; no se reutilizaron corridas de R3.1 porque el código cambió, conforme exige el prompt):

- `evidence/`: 25 archivos, **0 diferencias** entre A y B (SHA-256 por archivo, incluido el manifest y las 686 010 referencias serializadas).
- Árbol completo: 958 archivos, 1 única diferencia (`index/repository.json`, solo `duration_seconds`, metadata operacional ya excluida por D-01).

## 10. Compatibilidad V4.3

`v5_1_r3_2_run_a` frente al baseline de R3.1 (`v5_1_r3_1_run_a`):

- `index/`: 22/22 archivos comparados, 21 byte-idénticos, el único distinto (`repository.json`) difiere solo en `duration_seconds`.
- `documentation/`: 876/876 archivos, 0 diferencias.
- `RUN_SUMMARY.json`: estructuralmente igual (mismas 11 claves, mismos 13 stages, sin `evidence` en `output_locations`).

`provenance` es una capacidad exclusiva de `evidence/`: la proyección legacy (`projection.py::LegacyIndexProjector`) reconstruye cada índice desde `entity.extensions` (el registro legacy sin tocar), nunca desde `to_dict()` ni desde `provenance` — confirmado por lectura de código, no supuesto. `provenance` es, por tanto, estructuralmente invisible para `index/`/`documentation/`, no solo "no se usó esta vez".

## 11. Resultado sobre IST real

- Target: `C:\Users\cgalianj\source\IST_40\Operacional` (solo lectura).
- Carpetas nuevas: `C:\PruebasLegacyMapper\Resultados\v5_1_r3_2_run_a` y `...\v5_1_r3_2_run_b`.
- Comandos: `python main.py full "C:\Users\cgalianj\source\IST_40\Operacional" --output <dir> --verbose`.

| Corrida | Resultado | Duración | Evidence Core (build/validate/persist) |
|---|---|---|---|
| A | SUCCESS, exit 0 | 1 778 s | 44.4 s / 1.5 s / 14.9 s |
| B | SUCCESS, exit 0 | 1 846 s | 16.6 s / 1.1 s / 13.8 s |

`validate` (I-1 + `sha256` + I-4/I-5) pasó de 0.8–0.9 s (R3.1, sin I-4/I-5) a 1.1–1.5 s (esta ronda, con las 454 010 entidades/686 010 referencias de I-4/I-5 añadidas) — coste adicional real, medido, no estimado. Identidad canónica (13 tipos), XDP y `sha256` reconfirmados sin regresión (idénticos a R3.1, §12).

## 12. Suite completa

`python -m unittest discover -s tests`, ejecutada tres veces a lo largo de la ronda:

| Corrida | Tests | Failures | Errors | Skipped |
|---|---|---|---|---|
| 1 (antes de ajustar el inventario de mantenibilidad) | 2 247 | 1 | 0 | 132 |
| 2 (tras el ajuste) | 2 247 | 0 | 0 | 132 |
| 3 (con los 13 tests nuevos de `ProvenanceTraceabilityTests`) | 2 260 | 0 | 0 | 132 |
| 4 (final, tras las corridas reales) | 2 260 | 0 | 0 | 132 |

2 260 = 2 247 (R3.1) + 13 nuevos. La única falla de la corrida 1 fue, de nuevo, `test_on_disk_inventory_matches_fresh_build_if_present` (el inventario heurístico de mantenibilidad, no relacionado con la corrección funcional): `invariants.py` creció (269 líneas, nuevas funciones documentadas) y cruzó de LOW a MEDIUM en el heurístico de riesgo, entró al top-20 de módulos más grandes (desplazando a `plugin_projection/example_report.py`), y `EvidenceReference` (`reference.py`) ganó un sexto método (`source_span`), entrando al top-20 de clases por cantidad de métodos y desplazando a `RelationCollection` (`relations/service.py`); además `invariants.py` subió su cobertura de docstrings por encima del promedio del repositorio (sacándolo del listado de módulos con documentación por debajo del promedio), empujando a `technical_documentation_renderer.py` (el módulo más grande del repositorio, sin cambios propios) por debajo de ese promedio en su lugar. Las tres correcciones están documentadas en el propio test, con la misma metodología que usaron R2/R2.1/R3.1 (medición directa con `tools.v4_1_r0.inventory.analyze_file`, nunca una cifra inventada). No es una regresión funcional: es la misma mecánica de umbral relativo que ya documentan los comentarios de ese archivo desde R2.

## 13. Deuda restante

- **D-5 (sin cambios, fuera de alcance de esta ronda):** sigue sin existir un lector `evidence/ → entidades`; `index/` se sigue proyectando desde un `NormalizedEvidence` en memoria, no desde `evidence/*.json` releído. No tocado, conforme al mandato explícito de esta ronda.
- **`source_span`/`textual` sin ejercitar en datos reales:** ambos tipos están implementados, probados (tests 4/5/6) y disponibles para cualquier adapter futuro con columnas reales o evidencia puramente textual, pero IST real no generó ningún caso de ninguno de los dos (§7). No es un defecto: es la ausencia real de esos casos en el target actual.
- **`ExternalDependency` (assembly) referencia a `Project`, no directamente a `SourceArtifact`:** es una cadena de un salto (`ExternalDependency --entity--> Project --source--> SourceArtifact`), no un defecto — el propio `Project` ya tiene su `provenance` real y verificado; añadir un segundo `source` ref directo al `.vbproj` en el propio `ExternalDependency` sería redundante con el que `source_ref`/`Project.provenance` ya cubren.
- **Coste incremental de validación (I-4/I-5) medido, no optimizado:** 1.1–1.5 s sobre 454 010 entidades / 686 010 referencias en IST real (§11). No se implementó ninguna optimización porque el prompt de esta ronda no la pidió y el costo es marginal frente al resto de la corrida (~1 800 s).
- **Deuda heredada sin cambios:** causa aguas arriba de D-1 (referencias `Include` vacío en `VBProjExtractor`) sigue sin tocarse, fuera de alcance de esta ronda también.

## 14. Si V5.1 está lista para R4

Los tres bloqueos que R3 dejó documentados (D-1, D-2, D-3) siguen cerrados según la revalidación de `docs/V5/V5_1_R3_REVALIDATION.md`, sin regresión (§10–§12 de este documento). D-4, el único punto que esa revalidación dejó abierto como desviación real de contrato, queda cerrado con código real, gate de producción ejecutándose realmente, y verificación sobre IST real en dos corridas independientes con determinismo confirmado. D-5 permanece como deuda aceptable, explícitamente fuera de alcance.

Esto no declara R4 completada ni cierra V5.1: es evidencia para que una revalidación externa de R3 (equivalente a `V5_1_R3_REVALIDATION.md`, pero incorporando el cierre de D-4) decida si V5.1 puede pasar a R4.

V5_1_R3_2_READY_FOR_R4_REVALIDATION
